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
        Schema::create('order_errors', function (Blueprint $table) {
            $table->id();
            $table->bigInteger("orders_id")->unsigned()->nullable();
            $table->foreign("orders_id")->references("id")->on("orders");
            $table->json('errors')->nullable()->default(null);
            $table->tinyInteger('status')->default(0);
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
        Schema::dropIfExists('order_errors');
    }
};
