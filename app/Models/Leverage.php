<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Leverage extends Model
{
    protected $fillable = [
        'leverage',
        'risk_percentage',
    ];
}
