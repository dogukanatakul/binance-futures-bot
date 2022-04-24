<?php

namespace App\Http\Middleware;

use App\Models\User;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class Auth
{
    public function handle(Request $request, Closure $next)
    {
        if ($request->filled('login') and $request->filled('time')) {
            $user = User::where('login_key', $request->login);
            if (!empty($user->first())) {
                $uuid = (string)\Illuminate\Support\Str::uuid();
                $user->update([
                    'login_key' => $uuid
                ]);
                Session::put('u2317', $uuid);
                Session::save();
                return redirect()->route('panel.dashboard');
            }
        }
        return $next($request);
    }
}
