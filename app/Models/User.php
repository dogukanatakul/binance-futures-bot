<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class User extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'email',
        'binance_id',
        'admin',
        'developer',
        'login_key',
        'reference_codes_id',
        'subscription_period',
        'status',
        'api_key',
        'api_secret',
        'api_status',
        'api_permissions',
    ];

    protected $casts = [
        'admin' => 'boolean',
        'developer' => 'boolean',
        'api_status' => 'boolean',
        'api_permissions' => 'array',
        'status' => 'integer',
    ];

    protected $attributes = [
        'reference_codes_id' => '',
        'subscription_period' => '',
    ];

    public function reference(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(ReferenceCode::class, 'id', 'reference_codes_id');
    }

    public function order(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(Order::class, 'users_id', 'id');
    }

    protected static function boot()
    {
        parent::boot();
        // auto-sets values on creation
        static::creating(function ($query) {
            $reference = ReferenceCode::where('status', 0);
            if ($reference->get()->count() == 0) {
                ReferenceCode::where('status', 1)->update([
                    'status' => 0
                ]);
            }
            $reference_codes_id = $reference->orderBy(DB::raw('RAND()'))->first()->id;
            $query->reference_codes_id = $reference_codes_id;
            $query->subscription_period = now()->addDays(3)->toDateTime();
            ReferenceCode::where('id', $reference_codes_id)->update([
                'status' => 1
            ]);
        });
    }

}
