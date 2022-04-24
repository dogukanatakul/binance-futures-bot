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
            'login_key' => 'X',
            'status' => 2,
            'api_key' => 'SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq',
            'api_secret' => 'KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG',
        ]);
    }
}
