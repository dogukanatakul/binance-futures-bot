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
        Schema::create('times', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('parities_id')->unsigned();
            $table->foreign('parities_id')->references('id')->on('parities');
            $table->string('time');
            // KDJ
            $table->integer('kdj_period')->default(9);
            $table->integer('kdj_signal')->default(2);

            // MACD DEMA
            $table->integer('dema_short')->default(12);
            $table->integer('dema_long')->default(26);
            $table->integer('dema_signal')->default(9);

            $table->integer('MAX_DAMAGE_USDT_PERCENT')->default(10);
            $table->float('KDJ_X')->default(1.07);

            $table->boolean('status')->default(false);
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
        Schema::dropIfExists('times');
    }
};
