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
        \App\Models\User::factory(50)->create();
        \App\Models\User::create([
            'email' => 'datakul@yandex.com',
            'login_key' => 'D',
            'status' => 1,
            'admin' => false,
            'api_key' => 'SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq',
            'api_secret' => 'KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG',
            'binance_id' => rand(111111111, 999999999)
        ]);
        \App\Models\User::create([
            'email' => 'mtolgacogurcu@gmail.com',
            'login_key' => 'X',
            'api_key' => '-',
            'api_secret' => '-',
            'status' => 2,
            'admin' => true,
        ]);
    }
}
