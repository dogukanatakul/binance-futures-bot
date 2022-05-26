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
                'dema_short' => 21,
                'dema_long' => 42,
                'dema_signal' => 80,
            ],
            'BNBUSDT' => [
                'kdj_period' => 30,
                'kdj_signal' => 5,
                'dema_short' => 12,
                'dema_long' => 26,
                'dema_signal' => 30,
            ],
            'XRPUSDT' => [
                'kdj_period' => 21,
                'kdj_signal' => 5,
                'dema_short' => 14,
                'dema_long' => 21,
                'dema_signal' => 50,
            ],
            'ETHUSDT' => [
                'kdj_period' => 26,
                'kdj_signal' => 5,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 50,
            ],
            'XLMUSDT' => [
                'kdj_period' => 21,
                'kdj_signal' => 4,
                'dema_short' => 21,
                'dema_long' => 26,
                'dema_signal' => 50,
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
