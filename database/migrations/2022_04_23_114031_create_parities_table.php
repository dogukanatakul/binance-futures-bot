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
            $table->integer('risk_percentage')->default(100);
            $table->decimal('min_price', 38, 22)->default(0);
            $table->decimal('max_price', 38, 22)->default(0);
            $table->decimal('min_amount', 38, 22)->default(0);
            $table->decimal('max_amount', 38, 22)->default(0);
            $table->integer('price_fraction')->default(0);
            $table->integer('amount_fraction')->default(0);
            $table->string('binance_status')->default('WAITING');
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
        Schema::dropIfExists('parities');
    }
};
