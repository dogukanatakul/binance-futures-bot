<?php

use Illuminate\Support\Facades\Route;

Route::post('/test', [\App\Http\Controllers\AppController::class, 'test']);

Route::group([
    'middleware' => [
        \App\Http\Middleware\ApiHeader::class,
    ]
], function () {
    Route::post('/get-order/{bot}', [\App\Http\Controllers\BotController::class, 'getOrder']);
    Route::post('/set-order/{bot}', [\App\Http\Controllers\BotController::class, 'setOrder']);
    Route::post('/proxy-order/{bot}', [\App\Http\Controllers\BotController::class, 'proxyOrder']);
    Route::post('/get-req-user', [\App\Http\Controllers\BotController::class, 'getReqUser']);
    Route::post('/set-req-user', [\App\Http\Controllers\BotController::class, 'setReqUser']);
    Route::post('/set-error', [\App\Http\Controllers\BotController::class, 'setError']);
    Route::post('/update-parity', [\App\Http\Controllers\BotController::class, 'updateParity']);
    Route::post('/delete-bots', [\App\Http\Controllers\BotController::class, 'deleteBots']);
});
