<?php

namespace Database\Seeders;

use App\Models\Parity;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ParitySeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $tokens = [
            'ADA',
            'AVAX',
            'ATOM',
            'ETH',
            'SOL',
            'BNB',
            'SHIB',
            'XRP',
            'DOGE',
            'LTC',
            'SAND',
            'GALA',
            'FTM',
            'WAVES',
            'EOS',
            'VET',
            'LINK',
            'CHZ',
            'TRX',
            'ENJ',
            'IOST',
            'IOTA',
            'CRV',
            'SUSHI',
            '1INCH',
            'ALGO',
            'BCH',
            'ETC',
            'BAT',
            'HOT',
            'DENT',
            'DASH',
            'ZEC',
            'MATIC',
            'XLM',
            'XMR',
            'QTUM',
            'ZIL',
            'DOT',
            'NEAR',
            'REEF',
            'MANA',
            'APE',
            'GRT',
            'THETA',
            'SRM',
            'TOMO',
            'KSM',
            'BAKE',
            'ONE',
            'ARPA',
            'SXP',
            'BAND'
        ];
        foreach ($tokens as $token) {
            Parity::create([
                'parity' => $token . "USDT",
                'source' => 'USDT',
                'token' => $token
            ]);
        }
    }
}
