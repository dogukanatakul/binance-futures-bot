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
            $table->bigInteger('orders_id')->unsigned();
            $table->foreign('orders_id')->references('id')->on('orders');
            $table->decimal("price", 38, 22);
            $table->decimal("quantity", 38, 22);
            $table->decimal("balance", 38, 22);
            $table->string('side');
            $table->string('position_side');
            $table->tinyInteger('profit')->default(0);
            $table->timestamp('start');
            $table->timestamp('finish')->nullable()->default(null);
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
