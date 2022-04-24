<?php

use Illuminate\Support\Facades\Route;


Route::get('/', [\App\Http\Controllers\AppController::class, 'home'])->name('home')->middleware([\App\Http\Middleware\Auth::class, \App\Http\Middleware\CheckAuth::class]);
Route::post('/', [\App\Http\Controllers\AuthController::class, 'auth'])->name('login')->middleware([\App\Http\Middleware\CheckAuth::class]);

Route::group([
    'as' => 'panel.',
    'middleware' => [
        \App\Http\Middleware\CheckAuth::class,
    ]
], function () {

    Route::get('/binance', [\App\Http\Controllers\AppController::class, 'binance'])->name('binance');
    Route::post('/binance', [\App\Http\Controllers\AppController::class, 'binanceSave'])->name('binance_save');
    Route::get('/binance-waiting', [\App\Http\Controllers\AppController::class, 'binanceWaiting'])->name('binance_waiting');
    Route::get('/dashboard', [\App\Http\Controllers\AppController::class, 'dashboard'])->name('dashboard');
    Route::get('/new-order', [\App\Http\Controllers\AppController::class, 'newOrder'])->name('new_order');
    Route::post('/new-order', [\App\Http\Controllers\AppController::class, 'orderSave'])->name('order_save');

});
