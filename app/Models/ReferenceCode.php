<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ReferenceCode extends Model
{
    protected $fillable = [
        'id',
        'code',
        'email',
        'status',
    ];
}
