<?php

namespace Database\Seeders;

use App\Models\Parity;
use App\Models\Time;
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
                'kdj_period' => '20',
                'kdj_signal' => '6',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '26'
            ],
            'BNBUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '5',
                'dema_short' => '12',
                'dema_long' => '26',
                'dema_signal' => '11'
            ],
            'ETHUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '5',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '18'
            ],
            'XRPUSDT' => [
                'kdj_period' => '30',
                'kdj_signal' => '6',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '21'
            ],
            'SANDUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '5',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '21'
            ],
            'DOTUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '21'
            ],
            'HOTUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '5',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '21'
            ],
            'DOGEUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '6',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '21'
            ],
            'SHIBAUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '7',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '26'
            ],
            'GALAUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '11',
                'dema_short' => '26',
                'dema_long' => '35',
                'dema_signal' => '30'
            ],
            'ETCUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '18'
            ],
            'MATICUSDT' => [
                'kdj_period' => '30',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '26'
            ],
            'FTMUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '5',
                'dema_short' => '12',
                'dema_long' => '26',
                'dema_signal' => '15'
            ],
            'AXSUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '4',
                'dema_short' => '9',
                'dema_long' => '26',
                'dema_signal' => '15'
            ],
            'APEUSDT' => [
                'kdj_period' => '28',
                'kdj_signal' => '4',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '20'
            ],
            'GMTUSDT' => [
                'kdj_period' => '20',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '15'
            ],
            'ALICEUSDT' => [
                'kdj_period' => '24',
                'kdj_signal' => '8',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '20'
            ],
            'DYDXUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '30'
            ],
            'CRVUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '26'
            ],
            'ALGOUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '12',
                'dema_short' => '25',
                'dema_long' => '50',
                'dema_signal' => '75'
            ],
            'BLZUSDT' => [
                'kdj_period' => '30',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '14'
            ],
            'ENJUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '26'
            ],
            'SOLUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '14'
            ],
            'SXPUSDT' => [
                'kdj_period' => '25',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '14'
            ],
            'XLMUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '4',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '50'
            ],
            'LTCUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '21'
            ],
            'CHZUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '25'
            ],
            'TRXUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '4',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '9'
            ],
            'ATOMUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '6',
                'dema_short' => '21',
                'dema_long' => '26',
                'dema_signal' => '19'
            ],
            'LINKUSDT' => [
                'kdj_period' => '30',
                'kdj_signal' => '9',
                'dema_short' => '26',
                'dema_long' => '78',
                'dema_signal' => '60'
            ],
            'KNCUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '21'
            ],
            'EOSUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '6',
                'dema_short' => '14',
                'dema_long' => '21',
                'dema_signal' => '21'
            ],
            'DASHUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '7',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '26'
            ],
            'ZECUSDT' => [
                'kdj_period' => '26',
                'kdj_signal' => '5',
                'dema_short' => '14',
                'dema_long' => '26',
                'dema_signal' => '24'
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
