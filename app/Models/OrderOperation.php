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
        'K',
        'D',
        'J',
        'time'
    ];

    protected $casts = [
      'price' => 'float',
      'balance' => 'float',
      'quantity' => 'float',
      'K' => 'float',
      'D' => 'float',
      'J' => 'float',
      'time' => 'datetime',
    ];

    public function order(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Order::class, 'id', 'orders_id');
    }
}
