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
            $table->integer('short_trigger_min')->default(10); # shortta olduğunu algılaması için kaç kez short verisini beklesin
            $table->integer('reverse_delay')->default(3); # işlem longdan short a dönerse kaç kere short beklesin?
            $table->integer('risk_percentage')->default(0);
            $table->integer('status')->default(0);
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
