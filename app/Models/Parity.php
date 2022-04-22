<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Parity extends Model
{
    protected $fillable = [
      'parity',
      'source',
      'token',
      'risk_percentage',
      'status',
    ];
}
