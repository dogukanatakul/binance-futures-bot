<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * @return void
     */
    public function run()
    {
        $this->call(ReferenceSeeder::class);
        $this->call(ParitySeeder::class);
        $this->call(LeverageSeeder::class);
        $this->call(TimeSeeder::class);
//        \App\Models\User::factory(50)->create();
        \App\Models\User::create([
            'email' => 'datakul@yandex.com',
            'login_key' => 'X',
            'status' => 1,
            'admin' => true,
            'api_key' => 'l8FqzEGOW91yP139vjZKDMs6oZJse4Isl3emol6dAMwVwKhHvOwH5irOVBvBhsVc',
            'api_secret' => 'eMlTWnJKQypSF2nlpCoWqTv6zyXej2hjDt2e7iqTNQbMoRQW3mOp94bkowj1OAtg',
            'binance_id' => 95200230
        ]);
    }
}
