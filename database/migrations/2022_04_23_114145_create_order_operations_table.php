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
        Schema::create('order_operations', function (Blueprint $table) {
            $table->id();
            $table->bigInteger("orders_id")->unsigned();
            $table->foreign("orders_id")->references("id")->on("orders");
            $table->decimal("price", 38, 22)->nullable()->default(null);
            $table->decimal("quantity", 38, 22)->nullable()->default(null);
            $table->decimal("balance", 38, 22)->default(0);
            $table->string("side")->nullable()->default(null);
            $table->string("position_side")->nullable()->default(null);
            $table->string("action")->nullable()->default(null);
            $table->decimal("profit", 38, 22)->default(0);
            $table->decimal("commission", 38, 22)->default(0);

            $table->string("BRS")->nullable()->default(null);
            $table->string("BRS_M")->nullable()->default(null);
            $table->string("BRS_T")->nullable()->default(null);
            $table->string("BRS_C")->nullable()->default(null);

            $table->dateTime("time");
            $table->integer('line')->default(0);
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
        Schema::dropIfExists('order_operations');
    }
};
