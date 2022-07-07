<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class ChartLog extends Model
{
    use SoftDeletes;
    protected $fillable = [
      'parities_id',
      'times_id',
      'orders_id',
      'K',
      'D',
      'J',
    ];
}
