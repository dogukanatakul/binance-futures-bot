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
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'BNBUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'ETHUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '4',
            ],
            'XRPUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'SANDUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'DOTUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '5',
            ],
            'HOTUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '5',
            ],
            'DOGEUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '5',
            ],
            'SHIBAUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'GALAUSDT' => [
                'kdj_period' => '12',
                'kdj_signal' => '3',
            ],
            'ETCUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'MATICUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'FTMUSDT' => [
                'kdj_period' => '12',
                'kdj_signal' => '5',
            ],
            'AXSUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'APEUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '4',
            ],
            'GMTUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'ALICEUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'DYDXUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '5',
            ],
            'CRVUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'ALGOUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '2',
            ],
            'BLZUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'ENJUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '5',
            ],
            'SOLUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'SXPUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'XLMUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'LTCUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'CHZUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'TRXUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'ATOMUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '5',
            ],
            'LINKUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '5',
            ],
            'KNCUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'EOSUSDT' => [
                'kdj_period' => '15',
                'kdj_signal' => '6',
            ],
            'DASHUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '4',
            ],
            'ZECUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'AVAXUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'BANDUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '4',
            ],
            'BATUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '5',
            ],
            'BCHUSDT' => [
                'kdj_period' => '21',
                'kdj_signal' => '4',
            ],
            'CTSIUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '4',
            ],
            'FLMUSDT' => [
                'kdj_period' => '15',
                'kdj_signal' => '5',
            ],
            'GRTUSDT' => [
                'kdj_period' => '9',
                'kdj_signal' => '3',
            ],
            'IOSTUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'IOTAUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '3',
            ],
            'KAVAUSDT' => [
                'kdj_period' => '11',
                'kdj_signal' => '5',
            ],
            'OCEANUSDT' => [
                'kdj_period' => '14',
                'kdj_signal' => '5',
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
