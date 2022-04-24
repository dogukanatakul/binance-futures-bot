<?php
use Illuminate\Support\Facades\Route;

Route::post('/get-order/{bot}', [\App\Http\Controllers\BotController::class, 'getOrder'])->name('binance');

