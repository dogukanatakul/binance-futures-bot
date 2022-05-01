<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class CheckLanguage
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
        if (isset($_SERVER['HTTP_ACCEPT_LANGUAGE'])) {
            // kullanıcı dilini alabiliyorsak
            $browserLocale = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 5);
            if (!array_key_exists('locale', $request->route()->parameters())) {
                // dil uzantısı yoksa
                if (in_array($browserLocale, config('app.available_locales'))) {
                    // dil desteği varsa
                    app()->setLocale($browserLocale);
                    $next($request);
                } else {
                    // dil desteği yoksa
                    app()->setLocale("en-US");
                    $next($request);
                }
            } else {
                // dil uzantısı varsa
                if (!in_array($request->route()->parameters()['locale'], config('app.available_locales'))) {
                    // dil artık geçerli değilse
                    if (in_array($browserLocale, config('app.available_locales'))) {
                        // dil desteği varsa
                        app()->setLocale($browserLocale);
                        $next($request);
                    } else {
                        // dil desteği yoksa
                        app()->setLocale("en-US");
                        $next($request);
                    }
                } else {
                    // dil halen geçerli ise
                    app()->setLocale($request->route()->parameters()['locale']);
                }
            }
        }
        return $next($request);
    }
}
