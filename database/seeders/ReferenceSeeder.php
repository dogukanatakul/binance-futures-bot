<?php

namespace Database\Seeders;

use App\Models\ReferenceCode;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ReferenceSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $codes = [
            'CPA_00K3PGAZTF' => 'mtolgacogurcu@gmail.com',
        ];
        foreach ($codes as $code => $email) {
            ReferenceCode::create([
                'code' => $code,
                'email' => $email,
            ]);
        }
    }
}
