<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    protected $fillable = [
        'users_id',
        'parities_id',
        'leverages_id',
        'times_id',
        'percent',
        'start',
        'finish',
        'status',
        'bot',
    ];

    public function leverage(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Leverage::class, 'id', 'leverages_id');
    }

    public function parity(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Parity::class, 'id', 'parities_id');
    }

    public function time(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Time::class, 'id', 'times_id');
    }

    public function user(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(User::class, 'id', 'users_id');
    }
}
