<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TimeIndicatorPeriod extends Model
{
    use HasFactory;

    protected $fillable = [
        'times_id',
        'microtime',
        'values',
    ];
    protected $casts = [
        'values' => 'array',
        'microtime' => 'integer',
    ];
}
