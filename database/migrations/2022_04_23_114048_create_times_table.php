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
            $table->bigInteger('sub_times_id')->nullable()->default(null)->unsigned();
            $table->foreign('sub_times_id')->references('id')->on('times');
            // MANUAL
            $table->integer('start_diff')->default(0); # longa gidişte emir açma yüzde farkı
            $table->integer('fake_reverse')->default(2); # tetiklemede düşüş olursa kaç kere düşüşü deyit etsin
            $table->integer('trigger_diff')->default(0); # tetikleme kaç% fark olursa devreye girsin
            $table->integer('start_trigger_min')->default(5); # shortta olduğunu algılaması için kaç kez short verisini beklesin
            $table->integer('reverse_delay')->default(0); # işlem longdan short a dönerse kaç kere short beklesin?
            $table->integer('risk_percentage')->default(0);
            // T3
            $table->integer('t3_length')->default(2);
            $table->float("t3_volume_factor")->default(0.7);
            // KDJ
            $table->integer('kdj_period')->default(9);
            $table->integer('kdj_signal')->default(2);
            // Chandelier Exit
            $table->integer('atr_period')->default(22);
            $table->float('atr_multiplier')->default(3.0);

            // MACD DEMA
            $table->integer('dema_short')->default(12);
            $table->integer('dema_long')->default(26);
            $table->integer('dema_signal')->default(9);

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
