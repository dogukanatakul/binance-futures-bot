<?php

namespace App\Jobs;

use App\Models\Bot;
use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

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
            if (!empty($bot = Bot::orderBy('id', 'DESC')->first())) {
                $order->bot = $bot->uuid;
                $order->status = 1;
                $order->save();
                $bot->delete();
            }
        }
        return true;
    }
}
