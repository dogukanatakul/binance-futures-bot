<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Time extends Model
{
    protected $fillable = [
        'time',
        'start_diff',
        'trigger_diff',
        'risk_percentage',
        'short_trigger_min',
        'fake_reverse',
        'status',
    ];
}
