<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class OrderOperation extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'orders_id',
        'price',
        'quantity',
        'balance',
        'side',
        'position_side',
        'action',
        'profit',
        'commission',
        'BRS',
        'BRS_M',
        'BRS_T',
        'BRS_C',
        'time',
        'line',
    ];

    protected $casts = [
        'price' => 'float',
        'balance' => 'float',
        'quantity' => 'float',
        'profit' => 'float',
        'commission' => 'float',
        'time' => 'datetime',
        'line' => 'integer',
    ];

    public function order(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Order::class, 'id', 'orders_id');
    }
}
