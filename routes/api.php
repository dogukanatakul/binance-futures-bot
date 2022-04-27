<?php
use Illuminate\Support\Facades\Route;

Route::post('/get-order/{bot}', [\App\Http\Controllers\BotController::class, 'getOrder']);
Route::post('/set-order/{bot}', [\App\Http\Controllers\BotController::class, 'setOrder']);
Route::post('/get-req-user', [\App\Http\Controllers\BotController::class, 'getReqUser']);
Route::post('/set-req-user', [\App\Http\Controllers\BotController::class, 'setReqUser']);

