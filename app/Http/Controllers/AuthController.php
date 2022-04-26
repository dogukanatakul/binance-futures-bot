<?php

namespace App\Http\Controllers;

use App\Jobs\EmailAuth;
use App\Models\User;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    public function auth(Request $request)
    {
        $validator = validator()->make(request()->all(), [
            'email' => 'required|filled|email'
        ]);
        if ($validator->fails()) {
            return redirect()->back();
        }
        if (empty(User::where('email', $request->email)->first())) {
            User::create([
                'email' => $request->email
            ]);
        }
        EmailAuth::dispatch($request->email)->onQueue('email');
        return view('email.check');
    }
}
