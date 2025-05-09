<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Proxy extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'user',
        'password',
        'host',
        'port',
        'status',
    ];

    protected $casts = [
        'status' => 'boolean',
    ];
}
