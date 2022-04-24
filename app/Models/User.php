<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class User extends Model
{
    use HasFactory;

    protected $fillable = [
        'email',
        'login_key',
        'reference_codes_id',
        'subscription_period',
        'api_key',
        'api_secret',
    ];

    protected $attributes = [
        'reference_codes_id' => '',
        'subscription_period' => '',
    ];

    public function reference()
    {
        return $this->hasOne(ReferenceCode::class, 'id', 'reference_codes_id');
    }

    public function order()
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
