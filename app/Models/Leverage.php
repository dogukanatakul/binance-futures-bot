<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Leverage extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'leverage',
        'risk_percentage',
        'status'
    ];

    protected $casts = [
        'status' => 'boolean',
    ];
}
