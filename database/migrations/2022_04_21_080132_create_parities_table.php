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
        Schema::create('parities', function (Blueprint $table) {
            $table->id();
            $table->string('parity')->unique(); # DOGEUSDT
            $table->string('source'); # USDT
            $table->string('token'); # DOGE
            $table->integer('risk_percentage')->default(100);
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
        Schema::dropIfExists('parities');
    }
};
