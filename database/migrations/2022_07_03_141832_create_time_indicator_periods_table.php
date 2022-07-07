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
        Schema::create('time_indicator_periods', function (Blueprint $table) {
            $table->id();
            $table->bigInteger("times_id")->unsigned();
            $table->foreign("times_id")->references("id")->on("times");
            $table->bigInteger('microtime');
            $table->unique(['times_id', 'microtime'], 'period_unique');
            $table->json('values')->default(null);
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
        Schema::dropIfExists('time_indicator_periods');
    }
};
