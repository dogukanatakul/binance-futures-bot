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
        'version'
    ];


    protected static function boot()
    {
        parent::boot();
        // auto-sets values on creation
        static::creating(function ($query) {
            $query->version = config('app.bot_version');
        });
    }
}
