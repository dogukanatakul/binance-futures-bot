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
            'XRPUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 5,
                'dema_short' => 20,
                'dema_long' => 40,
                'dema_signal' => 20,
            ],
            'BANDUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 4,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 50,
            ],
            'AXSUSDT' => [
                'kdj_period' => 45,
                'kdj_signal' => 5,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 25,
            ],
            'CRVUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 4,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 50,
            ],
            'APEUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 7,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 50,
            ],
            'GMTUSDT' => [
                'kdj_period' => 70,
                'kdj_signal' => 6,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 25,
            ],
            'DYDXUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 3,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],

            'LTCUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 3,
                'dema_short' => 20,
                'dema_long' => 40,
                'dema_signal' => 20,
            ],
            'MATICUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 3,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],
            'ETHUSDT' => [
                'kdj_period' => 30,
                'kdj_signal' => 4,
                'dema_short' => 50,
                'dema_long' => 100,
                'dema_signal' => 25,
            ],
            '1INCHUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 6,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],
            'ALGOUSDT' => [
                'kdj_period' => 40,
                'kdj_signal' => 4,
                'dema_short' => 12,
                'dema_long' => 26,
                'dema_signal' => 21,
            ],
            'ALICEUSDT' => [
                'kdj_period' => 40,
                'kdj_signal' => 5,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],
            'BLZUSDT' => [
                'kdj_period' => 40,
                'kdj_signal' => 3,
                'dema_short' => 20,
                'dema_long' => 40,
                'dema_signal' => 20,
            ],
            'TRXUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 7,
                'dema_short' => 20,
                'dema_long' => 40,
                'dema_signal' => 20,
            ],
            'SOLUSDT' => [
                'kdj_period' => 60,
                'kdj_signal' => 4,
                'dema_short' => 40,
                'dema_long' => 80,
                'dema_signal' => 30,
            ],

            'PNTUSDT' => [
                'kdj_period' => 58,
                'kdj_signal' => 8,
                'dema_short' => 50,
                'dema_long' => 10,
                'dema_signal' => 30,
            ],
            'NEARUSDT' => [
                'kdj_period' => 40,
                'kdj_signal' => 3,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],
            'IOTAUSDT' => [
                'kdj_period' => 40,
                'kdj_signal' => 3,
                'dema_short' => 25,
                'dema_long' => 50,
                'dema_signal' => 25,
            ],
        ];
        foreach ($tokens as $token => $data) {
            $parity = Parity::create([
                'parity' => $token,
                'status' => true
            ]);
            $data['parities_id'] = $parity->id;
            $data['time'] = "30min";
            $data['status'] = true;
            Time::create($data);
        }
    }
}
