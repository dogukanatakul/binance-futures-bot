<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class ApiHeader
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
        if ($request->hasHeader('rndUuid') && $request->header('rndUuid') == "794d6f4b-f875-4ad1-aafa-b2e77a04bf58") {
            return $next($request);
        } else {
            return abort(404);
        }
    }
}
