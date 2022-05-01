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
        'volume_factor',
        'status',
    ];

    public function parity(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Parity::class, 'id', 'parities_id');
    }
}
