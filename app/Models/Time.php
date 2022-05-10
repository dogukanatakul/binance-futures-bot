<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Time extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'parities_id',
        'time',
        'start_diff',
        'trigger_diff',
        'risk_percentage',
        'start_trigger_min',
        'fake_reverse',
        't3_length',
        't3_volume_factor',

        'kdj_period',
        'kdj_signal',

        'atr_period',
        'atr_multiplier',

        'dema_short',
        'dema_long',
        'dema_signal',


        'sub_times_id',
        'status',
    ];

    protected $casts = [
        'kdj_period' => 'integer',
        'kdj_signal' => 'integer',

        't3_length' => 'integer',
        't3_volume_factor' => 'float',

        'atr_period' => 'integer',
        'atr_multiplier' => 'float',


        'dema_short' => 'float',
        'dema_long' => 'float',
        'dema_signal' => 'float',


        'status' => 'boolean',
    ];

    public function parity(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Parity::class, 'id', 'parities_id');
    }

    public function sub_time(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Time::class, 'id', 'sub_times_id');
    }
}
