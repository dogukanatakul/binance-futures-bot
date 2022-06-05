<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Bot extends Model
{
    use HasFactory;

    protected $fillable = [
        'uuid',
        'transfer',
        'version',
        'status',
        'signal'
    ];
    protected $casts = [
        'uuid' => 'string',
        'version' => 'string',
        'status' => 'boolean',
        'signal' => 'datetime',
    ];


    protected static function boot()
    {
        parent::boot();
        // auto-sets values on creation
        static::creating(function ($query) {
            $query->version = config('app.bot_version');
            $query->signal = now()->tz('Europe/Istanbul')->toDateTimeLocalString();
        });
    }
}
