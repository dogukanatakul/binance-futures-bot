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
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('proxies_id')->unsigned();
            $table->foreign('proxies_id')->references('id')->on('proxies');
            $table->bigInteger('users_id')->unsigned();
            $table->foreign('users_id')->references('id')->on('users');
            $table->bigInteger('parities_id')->unsigned();
            $table->foreign('parities_id')->references('id')->on('parities');
            $table->integer('leverage');
            $table->bigInteger('times_id')->unsigned();
            $table->foreign('times_id')->references('id')->on('times');
            $table->integer('percent')->default(0);
            $table->integer('profit')->default(0);
            $table->dateTime('finish')->nullable()->default(null);
            $table->tinyInteger('status')->default(0);
            $table->string('bot')->nullable()->default(null);
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
        Schema::dropIfExists('orders');
    }
};
