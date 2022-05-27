<?php

namespace Database\Seeders;

use App\Models\Parity;
use App\Models\Time;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ImportSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $tokens = [
            'BTCUSDT' => [
                'kdj_period' => 20,
                'kdj_signal' => 6,
                'dema_short' => 20,
                'dema_long' => 26,
                'dema_signal' => 25,
            ],
            'BNBUSDT' => [
                'kdj_period' => 21,
                'kdj_signal' => 5,
                'dema_short' => 12,
                'dema_long' => 26,
                'dema_signal' => 11,
            ],
            'XRPUSDT' => [
                'kdj_period' => 30,
                'kdj_signal' => 6,
                'dema_short' => 21,
                'dema_long' => 26,
                'dema_signal' => 21,
            ],
            'ETHUSDT' => [
                'kdj_period' => 26,
                'kdj_signal' => 5,
                'dema_short' => 21,
                'dema_long' => 26,
                'dema_signal' => 18,
            ],
            'AXSUSDT' => [
                'kdj_period' => 25,
                'kdj_signal' => 4,
                'dema_short' => 9,
                'dema_long' => 26,
                'dema_signal' => 15,
            ],
            'APEUSDT' => [
                'kdj_period' => 28,
                'kdj_signal' => 4,
                'dema_short' => 12,
                'dema_long' => 26,
                'dema_signal' => 20,
            ],
            'GMTUSDT' => [
                'kdj_period' => 29,
                'kdj_signal' => 5,
                'dema_short' => 14,
                'dema_long' => 26,
                'dema_signal' => 15,
            ],
        ];

        foreach ($tokens as $token => $data) {
            $parity = Parity::create([
                'parity' => $token,
                'status' => true
            ]);
            $data['parities_id'] = $parity->id;
            $data['time'] = "1hour";
            $data['status'] = true;
            Time::create($data);
        }
    }
}
