<?php

use Illuminate\Support\Facades\Route;


Route::get('/', [\App\Http\Controllers\AppController::class, 'home'])->name('home')->middleware([\App\Http\Middleware\Auth::class, \App\Http\Middleware\CheckAuth::class,'language']);
Route::post('/', [\App\Http\Controllers\AuthController::class, 'auth'])->name('login')->middleware([\App\Http\Middleware\CheckAuth::class,'language']);

Route::group([
    'as' => 'panel.',
    'middleware' => [
        \App\Http\Middleware\CheckAuth::class,
        'language'
    ]
], function () {
    Route::get('/binance', [\App\Http\Controllers\AppController::class, 'binance'])->name('binance');
    Route::post('/binance', [\App\Http\Controllers\AppController::class, 'binanceSave'])->name('binance_save');
    Route::get('/binance-waiting', [\App\Http\Controllers\AppController::class, 'binanceWaiting'])->name('binance_waiting');
    Route::get('/dashboard', [\App\Http\Controllers\AppController::class, 'dashboard'])->name('dashboard');
    Route::get('/new-order', [\App\Http\Controllers\AppController::class, 'newOrder'])->name('new_order');
    Route::post('/new-order', [\App\Http\Controllers\AppController::class, 'orderSave'])->name('order_save');
    Route::get('/stop-order/{id}', [\App\Http\Controllers\AppController::class, 'orderStop'])->name('order_stop');
    Route::get('/detail-order/{id}', [\App\Http\Controllers\AppController::class, 'orderDetail'])->name('order_detail');

    Route::group([
        'as' => 'admin.',
        'prefix' => 'admin',
        'middleware' => [
            \App\Http\Middleware\CheckAdmin::class,
        ]
    ], function () {
        Route::get('/', [\App\Http\Controllers\AdminController::class, 'dashboard'])->name('dashboard');
        Route::get('/users', [\App\Http\Controllers\AdminController::class, 'users'])->name('users');
        Route::get('/times', [\App\Http\Controllers\AdminController::class, 'times'])->name('times');
        Route::post('/times', [\App\Http\Controllers\AdminController::class, 'timeSave'])->name('time_save');
        Route::get('/orders', [\App\Http\Controllers\AdminController::class, 'orders'])->name('orders');
        Route::get('/leverages', [\App\Http\Controllers\AdminController::class, 'leverages'])->name('leverages');
    });

});
