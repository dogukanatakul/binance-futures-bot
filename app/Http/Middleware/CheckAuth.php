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
    public function handle(Request $request, Closure $next)
    {
        if (Session::has('u2317') && !empty($user = User::where('login_key', Session::get('u2317'))->first())) {
            if ((empty($user->api_key) || empty($user->api_secret)) && !in_array($request->route()->getActionMethod(), ['binance', 'binanceSave'])) {
                return redirect()->route('panel.binance');
            }
            if ($user->status == 1 && $request->route()->getActionMethod() != 'binanceWaiting') {
                return redirect()->route('panel.binance_waiting');
            } else if ($user->status != 1 && $request->route()->getActionMethod() == 'binanceWaiting') {
                return redirect()->route('panel.dashboard');

            }
            if (in_array($request->route()->getActionMethod(), ['home', 'login'])) {
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
