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
            // BRS
            $table->float('BRS_M')->default(1);
            $table->float('BRS_T')->default(1);
            $table->integer('BRS_LIMIT')->default(11);

            $table->float('MAX_DAMAGE_USDT_PERCENT')->default(1);

            $table->boolean('status')->default(false);
            $table->tinyInteger('export')->default(0);
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
