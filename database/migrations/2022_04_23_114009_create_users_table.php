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
            $table->boolean('admin')->default(false);
            $table->string('login_key')->nullable()->default(null);
            $table->string('api_key')->nullable()->default(null);
            $table->string('api_secret')->nullable()->default(null);
            $table->unique(['api_key', 'api_secret'], 'api_unique');
            $table->string('subscription')->default('trial');
            $table->dateTime('subscription_period')->nullable()->default(null);
            $table->decimal('balance', 38, 22)->default(0);
            $table->tinyInteger('status')->default(0);
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
