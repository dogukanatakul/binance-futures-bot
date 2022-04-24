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
        Schema::create('chart_logs', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('parities_id')->unsigned();
            $table->foreign('parities_id')->references('id')->on('parities');
            $table->bigInteger('times_id')->unsigned();
            $table->foreign('times_id')->references('id')->on('times');
            $table->bigInteger('orders_id')->unsigned();
            $table->foreign('orders_id')->references('id')->on('orders');
            $table->decimal("K", 38, 22)->default(0);
            $table->decimal("D", 38, 22)->default(0);
            $table->decimal("J", 38, 22)->default(0);
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
        Schema::dropIfExists('chart_logs');
    }
};
