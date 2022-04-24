<?php

namespace Database\Seeders;

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
            [
                'time' => '1min',
                'start_diff' => 15,
                'trigger_diff' => 20,
            ],
            [
                'time' => '5min',
                'start_diff' => 10,
                'trigger_diff' => 10,
            ],
            [
                'time' => '15min',
                'start_diff' => 15,
                'trigger_diff' => 15,
            ],
            [
                'time' => '30min',
                'start_diff' => 3,
                'trigger_diff' => 3,
            ],
            [
                'time' => '1hour',
                'start_diff' => 7,
                'trigger_diff' => 7,
            ],
            [
                'time' => '4hour',
                'start_diff' => 5,
                'trigger_diff' => 5,
            ],
        ];
        foreach ($times as $time) {
            Time::create($time);
        }
    }
}
