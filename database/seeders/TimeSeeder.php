<?php

namespace Database\Seeders;

use App\Models\Parity;
use App\Models\Time;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class TimeSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $times = [
//            [
//                'time' => '1min',
//                'trigger_diff' => 20,
//            ],
//            [
//                'time' => '5min',
//                'trigger_diff' => 10,
//            ],
//            [
//                'time' => '15min',
//                'trigger_diff' => 15,
//            ],
            [
                'time' => '30min',
                'trigger_diff' => 3,
                't3_length' => 14,
            ],
            [
                'time' => '1hour',
                'trigger_diff' => 7,
                't3_length' => 4,
            ],
            [
                'time' => '4hour',
                'trigger_diff' => 5,
                't3_length' => 3,
            ],
        ];

        $parities = Parity::get()->pluck('id');
        foreach ($parities as $parity) {
            foreach ($times as $time) {
                $time['parities_id'] = $parity;
                Time::create($time);
            }
        }
    }
}
