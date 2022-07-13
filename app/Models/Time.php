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
        'BRS_M',
        'BRS_T',
        'BRS_P1',
        'BRS_P2',
        'BRS_P3',
        'BRS_P4',
        'BRS_LIMIT',
        'MAX_DAMAGE_USDT_PERCENT',
        'status',
        'export_time',
        'export_time_status',
        'ceil',
    ];

    protected $casts = [
        'BRS_M' => 'float',
        'BRS_T' => 'float',
        'BRS_P1' => 'float',
        'BRS_P2' => 'float',
        'BRS_P3' => 'float',
        'BRS_P4' => 'float',
        'BRS_LIMIT' => 'integer',
        'MAX_DAMAGE_USDT_PERCENT' => 'float',
        'status' => 'boolean',
        'export_time' => 'integer',
        'export_time_status' => 'boolean',
        'ceil' => 'string',
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
