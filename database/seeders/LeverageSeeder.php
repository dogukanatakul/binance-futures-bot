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

        $leverages = [10 => true, 15 => true, 20 => false, 30 => false, 40 => false, 50 => false, 100 => false];
        foreach ($leverages as $leverage => $status) {
            Leverage::create([
                'leverage' => $leverage,
                'status' => $status
            ]);
        }
    }
}
