<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('chart_logs', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('times_id')->unsigned();
            $table->foreign('times_id')->references('id')->on('times');
            $table->bigInteger('parities_id')->unsigned();
            $table->foreign('parities_id')->references('id')->on('parities');
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
        Schema::dropIfExists('order_logs');
    }
};
