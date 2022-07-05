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
            $table->decimal('BRS_M', 38, 22)->default(0);
            $table->decimal('BRS_T', 38, 22)->default(0);
            $table->integer('BRS_LIMIT')->default(11);

            $table->float('MAX_DAMAGE_USDT_PERCENT')->default(1);

            $table->boolean('status')->default(false);
            $table->tinyInteger('export')->default(0); # 0: Boşta 1: İstek 2: Sonuç
            $table->bigInteger('export_time')->nullable()->default(null);
            $table->boolean('export_time_status')->default(false); # Eğer yeni M ve T değerleri girilmişse değiştirme.
            $table->string('ceil')->default("0");
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
