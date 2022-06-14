<?php

namespace App\Jobs;

use App\Models\Bot;
use App\Models\Order;
use App\Models\Proxy;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\DB;

class BotSetOrder implements ShouldQueue, ShouldBeUnique
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 120;

    /**
     * Create a new job instance.
     *
     * @return void
     */
    public function __construct()
    {
        //
    }

    /**
     * Execute the job.
     *
     * @return bool
     */
    public function handle(): bool
    {
        $orders = Order::where('status', 0)->get();
        foreach ($orders as $order) {
            if (!empty($bot = Bot::orderBy('signal', 'DESC')->where('version', config('app.bot_version'))->where('status', false)->first())) {
                $order->bot = $bot->uuid;
                $order->status = 1;
                $order->save();
                sleep(1);
                $bot->status = true;
                $bot->save();
            }
        }
        Proxy::where('status', false)
            ->where('updated_at', '>', now()->tz('Europe/Istanbul')->subMinutes(1)->toDateTimeLocalString())
            ->update([
                'status' => true
            ]);
        Bot::where('version', '!=', config('app.bot_version'))->where('status', false)->delete();
        Bot::where('signal', '<', now()->tz('Europe/Istanbul')->subMinutes(2))->where('status', false)->delete();
        $fails = Bot::where('signal', '<', now()->tz('Europe/Istanbul')->subMinutes(2)->toDateTimeLocalString())
            ->where('status', true)
            ->get();
        foreach ($fails as $fail) {
            DB::beginTransaction();
            if (!empty($order = Order::where('bot', $fail->uuid)->whereIn('status', [1, 2])->first())) {
                if (!empty($bot = Bot::orderBy('signal', 'DESC')->where('version', config('app.bot_version'))->where('status', false)->first())) {
                    $bot->status = true;
                    $bot->transfer = $fail->uuid;
                    $bot->save();
                    $fail->delete();
                    $order->bot = $bot->uuid;
                    $order->save();
                    DB::commit();
                }
            } else {
                $fail->delete();
                DB::commit();
            }
        }
        return true;
    }
}
