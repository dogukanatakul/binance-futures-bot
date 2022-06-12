<?php

namespace App\Http\Controllers;

use App\Jobs\EmailAdminUserVerify;
use App\Models\Bot;
use App\Models\Order;
use App\Models\OrderError;
use App\Models\OrderOperation;
use App\Models\Parity;
use App\Models\Proxy;
use App\Models\User;
use Illuminate\Http\Request;

class BotController extends Controller
{
    public function getOrder($bot): \Illuminate\Http\JsonResponse
    {
        Bot::where('uuid', $bot)->update(['signal' => now()->tz('Europe/Istanbul')->toDateTimeLocalString()]);
        if (!empty($order = Order::with(['order_operation', 'user', 'parity', 'time' => function ($q) {
            $q->with('sub_time');
        }, 'proxy', 'bots'])->where('bot', $bot)->whereIn('status', [1, 2])->first())) {
            return response()->json([
                'bot' => $order->bot,
                'api_key' => $order->user->api_key,
                'api_secret' => $order->user->api_secret,
                'leverage' => $order->leverage,
                'percent' => $order->percent,
                'profit' => $order->profit,
                'parity' => $order->parity->parity,
                'MAX_DAMAGE_USDT_PERCENT' => $order->time->MAX_DAMAGE_USDT_PERCENT,
                'KDJ_X' => $order->time->KDJ_X,
                'kdj_period' => $order->time->kdj_period,
                'kdj_signal' => $order->time->kdj_signal,
                'dema_short' => $order->time->dema_short,
                'dema_long' => $order->time->dema_long,
                'dema_signal' => $order->time->dema_signal,
                'time' => $order->time->time,
                'proxy' => [
                    'http' => "http://" . $order->proxy->user . ":" . $order->proxy->password . "@" . $order->proxy->host . ":" . $order->proxy->port,
                    'https' => "http://" . $order->proxy->user . ":" . $order->proxy->password . "@" . $order->proxy->host . ":" . $order->proxy->port
                ],
                'status' => $order->status,
                'transfer' => $order->bots->transfer,
                'last_operation' => $order->order_operation->count() > 0 ? $order->order_operation->last()->action : null,
                'version' => config('app.bot_version')
            ]);
        } else {
            if (empty(Bot::where('uuid', $bot)->first())) {
                Bot::create([
                    'uuid' => $bot
                ]);
            }
            return response()->json([
                'status' => 0,
                'version' => config('app.bot_version')
            ]);
        }
    }

    public function proxyOrder($bot): \Illuminate\Http\JsonResponse
    {
        if (!empty($order = Order::where('bot', $bot)->first())) {
            $activeOrders = Order::whereIn('status', [0, 1, 2])->get()->pluck('proxies_id');
            Proxy::where('id', $order->proxies_id)->update([
                'status' => false
            ]);
            $proxy = Proxy::whereNotIn('id', $activeOrders->toArray())->where('status', true)->orderByRaw("RAND()")->first();
            if (empty($proxy)) {
                return response()->json([
                    'status' => 'fail'
                ]);
            }
            $order->proxies_id = $proxy->id;
            $order->save();
            return response()->json([
                'proxy' => [
                    'http' => "http://" . $proxy->user . ":" . $proxy->password . "@" . $proxy->host . ":" . $proxy->port,
                    'https' => "http://" . $proxy->user . ":" . $proxy->password . "@" . $proxy->host . ":" . $proxy->port
                ],
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
            if ($request->action == "ORDER_START_WAITING") {
                OrderOperation::where('updated_at', '<', now()->tz('Europe/Istanbul')->subMinutes(1)->toDateTimeLocalString())
                    ->where('action', 'ORDER_START_WAITING')
                    ->where('orders_id', $order->id)
                    ->forceDelete();
            }
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
            if (!empty($order = Order::where('bot', $request->bot)->first())) {
                $order->status = 3;
                $order->finish = now()->tz('Europe/Istanbul')->toDateTimeString();
                $order->save();
                OrderError::create([
                    'orders_id' => $order->id,
                    'errors' => $request->errors
                ]);
            } else {
                $errors = $request->errors;
                $errors[] = $request->bot;
                OrderError::create([
                    'errors' => $errors
                ]);
            }

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

    public function deleteBots(): \Illuminate\Http\JsonResponse
    {
        Bot::where('status', false)->delete();
        return response()->json([
            'status' => 'success'
        ]);
    }
}
