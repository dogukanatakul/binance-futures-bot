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
        'kdj_period',
        'kdj_signal',
        'dema_short',
        'dema_long',
        'dema_signal',

        'MAX_DAMAGE_USDT_PERCENT',

        'status',
    ];

    protected $casts = [
        'kdj_period' => 'integer',
        'kdj_signal' => 'integer',
        'dema_short' => 'float',
        'dema_long' => 'float',
        'dema_signal' => 'float',

        'MAX_DAMAGE_USDT_PERCENT' => 'integer',

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
