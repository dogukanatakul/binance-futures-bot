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
//            'A4J253H7' => 'haliloffroad42@gmail.com',
//            '96505344' => 'otenemrah750@gmail.com',
//            '36560539' => 'kahiyeramazan0@gmail.com',
//            'WOZNZDTT' => 'mustafakalaycikonya@gmail.com',
//            'CPA_00U819MFJH' => 'yusufsalih16@gmail.com',
        ];
        foreach ($codes as $code => $email) {
            ReferenceCode::create([
                'code' => $code,
                'email' => $email,
            ]);
        }
    }
}
