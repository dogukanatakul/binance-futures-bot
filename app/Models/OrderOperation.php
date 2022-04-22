<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class OrderOperation extends Model
{
    protected $fillable = [
        'orders_id',
        'price',
        'quantity',
        'balance',
        'side',
        'position_side',
        'profit',
        'start',
        'finish',
    ];
}
