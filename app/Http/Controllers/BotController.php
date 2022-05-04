<?php

namespace App\Http\Controllers;

use App\Jobs\EmailAdminUserVerify;
use App\Models\Order;
use App\Models\OrderError;
use App\Models\OrderOperation;
use App\Models\Parity;
use App\Models\Proxy;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class BotController extends Controller
{
    public function getOrder($bot): \Illuminate\Http\JsonResponse
    {
        if ($bot == "new") {
            $uuid = (string)Str::uuid();
            $order = Order::whereHas('user', function ($q) {
                $q->where('api_status', true);
            })->whereNull('bot')->limit(1)->update([
                'bot' => $uuid,
                'status' => 1,
            ]);
            if ($order == 0) {
                return response()->json([
                    'status' => 0,
                    'version' => config('app.bot_version')
                ]);
            } else {
                $order = Order::with(['user', 'leverage', 'parity', 'time', 'proxy'])->where('bot', $uuid)->first();
                return response()->json([
                    'bot' => $order->bot,
                    'api_key' => $order->user->api_key,
                    'api_secret' => $order->user->api_secret,
                    'leverage' => $order->leverage->leverage,
                    'percent' => $order->percent,
                    'parity' => $order->parity->parity,
                    'start_trigger_min' => $order->time->start_trigger_min,
                    'fake_reverse' => $order->time->fake_reverse,
                    'reverse_delay' => $order->time->reverse_delay,
                    't3_length' => $order->time->t3_length,
                    'volume_factor' => $order->time->volume_factor,
                    'kdj_period' => $order->time->kdj_period,
                    'kdj_signal' => $order->time->kdj_signal,
                    'time' => $order->time->time,
                    'proxy' => [
                        'http' => "http://" . $order->proxy->user . ":" . $order->proxy->password . "@" . $order->proxy->host . ":" . $order->proxy->port,
                        'https' => "http://" . $order->proxy->user . ":" . $order->proxy->password . "@" . $order->proxy->host . ":" . $order->proxy->port
                    ],
                    'status' => $order->status,
                    'version' => config('app.bot_version')
                ]);
            }
        } else if (!empty($order = Order::with(['leverage', 'parity', 'time'])->where('bot', $bot)->first())) {
            return response()->json([
                'bot' => $order->bot,
                'start_diff' => $order->time->start_diff,
                'trigger_diff' => $order->time->trigger_diff,
                'start_trigger_min' => $order->time->start_trigger_min,
                'fake_reverse' => $order->time->fake_reverse,
                'reverse_delay' => $order->time->reverse_delay,
                't3_length' => $order->time->t3_length,
                'volume_factor' => $order->time->volume_factor,
                'kdj_period' => $order->time->kdj_period,
                'kdj_signal' => $order->time->kdj_signal,
                'status' => $order->status,
                'version' => config('app.bot_version')
            ]);
        }
        return response()->json([
            'status' => 'fail'
        ]);
    }

    public function setOrder($bot, Request $request): \Illuminate\Http\JsonResponse
    {
        if (!empty($order = Order::where('bot', $bot)->first())) {
            $orderOperation = $request->toArray();
            $orderOperation['orders_id'] = $order->id;
            OrderOperation::create($orderOperation);
            if ((!empty($stopOrder = Order::where('status', 2)->where('bot', $bot)->first())) and $request->filled('action') and ($request->action == "STOP" or $request->action == "CLOSE" or $request->action == "CLOSE_TRIGGER")) {
                $stopOrder->status = 3;
                $stopOrder->finish = now()->toDateTime();
                $stopOrder->save();
                return response()->json([
                    'status' => 'success'
                ]);
            } else if ((!empty($manualStop = Order::whereIn('status', [1, 2])->where('bot', $bot)->first())) and $request->action == "MANUAL_STOP") {
                $manualStop->status = 3;
                $manualStop->finish = now()->toDateTime();
                $manualStop->save();
                return response()->json([
                    'status' => 'success'
                ]);
            }
            return response()->json([
                'status' => 'fail'
            ]);
        }
        return response()->json([
            'status' => 'fail'
        ]);
    }

    public function getReqUser(): \Illuminate\Http\JsonResponse
    {
        $orders = Order::whereIn('status', [0, 1, 2])->get()->pluck('users_id');
        $users = User::select(['id', 'api_key', 'api_secret'])->whereNotIn('id', $orders->toArray())->whereNotNull('api_key')->whereNotNull('api_secret')->get();
        $proxies = collect(Proxy::limit($users->count())->where('status', 1)->orderByRaw("RAND()")->get())->map(function ($item) {
            return [
                'http' => "http://" . $item->user . ":" . $item->password . "@" . $item->host . ":" . $item->port,
                'https' => "http://" . $item->user . ":" . $item->password . "@" . $item->host . ":" . $item->port
            ];
        });
        return response()->json([
            'users' => $users->toArray(),
            'proxies' => $proxies->toArray()
        ]);
    }

    public function setReqUser(Request $request): \Illuminate\Http\JsonResponse
    {
        $orderStopStatus = false;
        $user = User::where('id', $request->user)->first();
        if ($request->filled('permissions') && count($request->permissions) > 0) {
            $orderStopStatus = true;
            $user->api_status = false;
            $user->api_permissions = $request->permissions;
        } else if ($request->filled('status') && $request->status == 'fail') {
            $orderStopStatus = true;
            $user->api_status = false;
            $user->status = 0;
            $user->api_permissions = [];
        } else {
            if ($user->status == 0) {
                foreach (User::where('admin', true)->get() as $admin) {
                    EmailAdminUserVerify::dispatch($admin->email)->onQueue('email');
                }
                $user->status = 1;
            }
            $user->api_status = true;
            $user->api_permissions = [];
        }
        $user->save();
        if ($orderStopStatus) {
            Order::where('users_id', $user->id)->whereIn('status', [0, 1])->update([
                'status' => 2
            ]);
        }
        return response()->json([
            'status' => 'success'
        ]);
    }

    public function setError(Request $request): \Illuminate\Http\JsonResponse
    {
        $validator = validator()->make(request()->all(), [
            'bot' => 'required|filled',
            'errors' => 'required|filled',
        ]);
        if ($validator->fails()) {
            return abort(404);
        }
        try {
            $order = Order::where('bot', $request->bot)->first();
            $order->status = 3;
            $order->finish = now()->toDateTimeString();
            $order->save();
            OrderError::create([
                'orders_id' => $order->id,
                'errors' => $request->errors
            ]);
        } catch (\Exception $e) {
            report($e);
            return response()->json([
                'status' => 'fail'
            ]);
        }
        return response()->json([
            'status' => 'success'
        ]);
    }

    public function updateParity(Request $request): \Illuminate\Http\JsonResponse
    {
        $validator = validator()->make(request()->all(), [
            'min_price' => 'required|filled',
            'max_price' => 'required|filled',
            'max_amount' => 'required|filled',
            'min_amount' => 'required|filled',
            'price_fraction' => 'required|filled',
            'amount_fraction' => 'required|filled',
            'binance_status' => 'required|filled',
            'parity' => 'required|filled',
        ]);
        if ($validator->fails()) {
            return abort(404);
        } else {
            try {
                if (!empty($parity = Parity::where('parity', $request->parity)->first())) {
                    $parity->update($request->toArray());
                }
                return response()->json([
                    'status' => 'success'
                ]);
            } catch (\Exception $exception) {
                report($exception);
                return response()->json([
                    'status' => 'fail'
                ]);
            }
        }
    }
}
