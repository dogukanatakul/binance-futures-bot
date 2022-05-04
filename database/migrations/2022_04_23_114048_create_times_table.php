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
            $table->integer('start_diff')->default(0); # longa gidişte emir açma yüzde farkı
            $table->integer('fake_reverse')->default(2); # tetiklemede düşüş olursa kaç kere düşüşü deyit etsin
            $table->integer('trigger_diff')->default(0); # tetikleme kaç% fark olursa devreye girsin
            $table->integer('start_trigger_min')->default(5); # shortta olduğunu algılaması için kaç kez short verisini beklesin
            $table->integer('reverse_delay')->default(2); # işlem longdan short a dönerse kaç kere short beklesin?
            $table->integer('risk_percentage')->default(0);
            $table->integer('t3_length')->default(2);
            $table->decimal("volume_factor", 3, 2)->default(0.7);
            $table->integer('kdj_period')->default(9);
            $table->integer('kdj_signal')->default(2);
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
