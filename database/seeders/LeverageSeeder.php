<?php

namespace Database\Seeders;

use App\Models\Leverage;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class LeverageSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {

        $leverages = [5, 10, 15];
        foreach ($leverages as $leverage) {
            Leverage::create([
                'leverage' => $leverage
            ]);
        }
    }
}
