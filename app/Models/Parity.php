<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Parity extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'parity',
        'risk_percentage',
        'binance_status',
        'status',
        'min_price',
        'max_price',
        'min_amount',
        'max_amount',
        'price_fraction',
        'amount_fraction',
    ];

    protected $casts = [
        'min_price' => 'float',
        'max_price' => 'float',
        'min_amount' => 'float',
        'max_amount' => 'float',
        'price_fraction' => 'integer',
        'amount_fraction' => 'integer',
        'status' => 'boolean',
    ];

    public function time(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(Time::class, 'parities_id', 'id');
    }

}
