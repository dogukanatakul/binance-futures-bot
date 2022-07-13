<?php

namespace App\Http\Middleware;

use App\Models\User;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class CheckAuth
{
    /**
     * Handle an incoming request.
     *
     * @param \Illuminate\Http\Request $request
     * @param \Closure(\Illuminate\Http\Request): (\Illuminate\Http\Response|\Illuminate\Http\RedirectResponse)  $next
     * @return \Illuminate\Http\Response|\Illuminate\Http\RedirectResponse
     */
    public function handle(Request $request, Closure $next): \Illuminate\Http\Response|\Illuminate\Http\RedirectResponse
    {
        if (Session::has('u2317') && !empty($user = User::where('login_key', Session::get('u2317'))->where('updated_at', '>', now()->tz('Europe/Istanbul')->subMinutes(5)->toDateTimeLocalString())->first())) {
            if ($user->status == 0 && $user->api_status == 0 && !in_array($request->route()->getActionMethod(), ['binance', 'binanceSave'])) {
                return redirect()->route('panel.binance');
            } else if ($user->status == 1 && $request->route()->getActionMethod() != 'binanceWaiting') {
                return redirect()->route('panel.binance_waiting');
            } else if ($user->api_status && $user->status == 2 && $request->route()->getActionMethod() == 'binanceWaiting') {
                return redirect()->route('panel.dashboard');
            } else if (in_array($request->route()->getActionMethod(), ['home', 'login'])) {
                return redirect()->route('panel.dashboard');
            }
            return $next($request);
        } else {
            if (!in_array($request->route()->getActionMethod(), ['home', 'auth'])) {
                Session::forget('u2317');
                Session::save();
                return redirect()->route('home');
            }
            return $next($request);
        }
    }
}
