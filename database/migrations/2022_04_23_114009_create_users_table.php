<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('email')->unique();
            $table->string('login_key')->nullable()->default(null);
            $table->bigInteger('binance_id')->unique()->nullable()->default(null);
            $table->string('api_key')->nullable()->default(null);
            $table->string('api_secret')->nullable()->default(null);
            $table->boolean('api_status')->default(false);
            $table->json('api_permissions')->default('[]');
            $table->unique(['api_key', 'api_secret'], 'api_unique');
            $table->dateTime('subscription_period')->nullable()->default(null);
            $table->tinyInteger('status')->default(0); # 0: Yeni üye | 1: binance onaylı | 2: admin onaylı
            $table->boolean('admin')->default(false);
            $table->bigInteger('reference_codes_id')->unsigned()->nullable()->default(null);
            $table->foreign('reference_codes_id')->references('id')->on('reference_codes');
            $table->softDeletes();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('users');
    }
};
