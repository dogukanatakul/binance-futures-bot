<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ChartLog extends Model
{
    protected $fillable = [
      'parities_id',
      'times_id',
      'orders_id',
      'K',
      'D',
      'J',
    ];
}
