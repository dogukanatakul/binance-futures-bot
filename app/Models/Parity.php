<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Parity extends Model
{
    use SoftDeletes;
    protected $fillable = [
      'parity',
      'source',
      'token',
      'risk_percentage',
      'status',
    ];
}
