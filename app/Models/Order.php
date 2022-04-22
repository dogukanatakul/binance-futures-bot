<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    protected $fillable = [
        'parities_id',
        'leverages_id',
        'times_id',
        'start',
        'finish',
        'status',
    ];
}
