<?php

namespace Database\Seeders;

use App\Models\Proxy;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Storage;

class ProxySeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $proxies = Storage::disk('public')->get('ips-data_center.txt');
        foreach (explode("\n", $proxies) as $proxy) {
            $proxy = explode(":", $proxy);
            Proxy::create([
                'user' => $proxy[2],
                'password' => $proxy[3],
                'host' => $proxy[0],
                'port' => $proxy[1],
            ]);
        }
    }
}
