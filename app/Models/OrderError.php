<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class OrderError extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'orders_id',
        'errors',
        'status',
    ];

    protected $casts = [
        'errors' => 'array'
    ];
}
