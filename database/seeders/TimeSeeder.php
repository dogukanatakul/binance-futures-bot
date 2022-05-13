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
            [
                'time' => '5min',
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
