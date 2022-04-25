<?php

namespace App\Http\Controllers;

use App\Models\Order;
use App\Models\OrderOperation;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class BotController extends Controller
{
    public function getOrder($bot, Request $request): \Illuminate\Http\JsonResponse
    {
        if ($request->hasHeader('neresi') && $request->header('neresi') == "dogunun+billurlari") {
            if ($bot == "new") {
                $uuid = (string)Str::uuid();
                $order = Order::whereNull('bot')->update([
                    'bot' => $uuid,
                    'status' => 1,
                ]);
                if ($order == 0) {
                    return response()->json([
                        'status' => 0,
                    ]);
                } else {
                    $order = Order::with(['user', 'leverage', 'parity', 'time'])->where('bot', $uuid)->first();
                    return response()->json([
                        'bot' => $order->bot,
                        'api_key' => $order->user->api_key,
                        'api_secret' => $order->user->api_secret,
                        'leverage' => $order->leverage->leverage,
                        'percent' => $order->percent,
                        'parity' => $order->parity->parity,
                        'source' => $order->parity->source,
                        'token' => $order->parity->token,
                        'short_trigger_min' => $order->time->short_trigger_min,
                        'fake_reverse' => $order->time->fake_reverse,
                        'reverse_delay' => $order->time->reverse_delay,
                        'time' => $order->time->time,
                        'status' => $order->status
                    ]);
                }
            } else if (!empty($order = Order::with(['leverage', 'parity', 'time'])->where('bot', $bot)->first())) {
                return response()->json([
                    'bot' => $order->bot,
                    'start_diff' => $order->time->start_diff,
                    'trigger_diff' => $order->time->trigger_diff,
                    'short_trigger_min' => $order->time->short_trigger_min,
                    'fake_reverse' => $order->time->fake_reverse,
                    'reverse_delay' => $order->time->reverse_delay,
                    'status' => $order->status,
                ]);
            }
        }

        return abort(404);
    }

    public function setOrder($bot, Request $request)
    {
        if ($request->hasHeader('neresi') && $request->header('neresi') == "dogunun+billurlari" && !empty($order = Order::where('bot', $bot)->first())) {
            $orderOperation = $request->toArray();
            $orderOperation['orders_id'] = $order->id;
            OrderOperation::create($orderOperation);
            if ((!empty($stopOrder = Order::where('status', 2)->where('bot', $bot)->first())) and $request->filled('action') and ($request->action == "STOP" or $request->action == "CLOSE" or $request->action == "CLOSE_TRIGGER")) {
                $stopOrder->status = 3;
                $stopOrder->finish = now()->toDateTime();
                $stopOrder->save();
            }

        }
    }
}
