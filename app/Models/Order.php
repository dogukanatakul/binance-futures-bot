<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Order extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'proxies_id',
        'users_id',
        'parities_id',
        'leverage',
        'times_id',
        'percent',
        'profit',
        'start',
        'finish',
        'status',
        'bot',
    ];

    protected $casts = [
        'profit' => 'integer',
        'start' => 'datetime',
        'finish' => 'datetime',
    ];

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

    public function bots(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Bot::class, 'uuid', 'bot');
    }

    public function order_operation(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(OrderOperation::class, 'orders_id', 'id');
    }

    public function proxy(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Proxy::class, 'id', 'proxies_id');
    }
}
