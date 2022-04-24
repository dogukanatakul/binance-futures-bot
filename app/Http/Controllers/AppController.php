<?php

namespace App\Http\Controllers;

use App\Models\Leverage;
use App\Models\Order;
use App\Models\Parity;
use App\Models\Time;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class AppController extends Controller
{
    protected $user;

    public function __construct()
    {
        $this->middleware(function ($request, $next) {
            if (session()->has('u2317')) {
                $this->user = Session::get('u2317');
            } else {
                $this->user = false;
            }
            return $next($request);
        });
    }


    public function home(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        return view('index');
    }

    public function binance(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::with('reference')->where('login_key', $this->user)->first();
        return view('binance', compact('user'));
    }

    public function binanceSave(Request $request): \Illuminate\Http\RedirectResponse
    {
        $validator = validator()->make(request()->all(), [
            'api_key' => 'required|filled|string',
            'api_secret' => 'required|filled|string'
        ]);
        if ($validator->fails()) {
            return redirect()->back();
        }
        try {
            User::where('login_key', $this->user)->update([
                'api_key' => $request->api_key,
                'api_secret' => $request->api_secret,
                'status' => 1,
            ]);
        } catch (\Exception $exception) {
            return redirect()->back();
        }
        return redirect()->route('panel.binance_waiting');
    }

    public function binanceWaiting(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        return view('binance_waiting');
    }

    public function dashboard(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::with('order')->where('login_key', $this->user)->first();
        return view('dashboard', compact('user'));
    }

    public function newOrder(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $parities = Parity::get()->pluck('parity');
        $leverages = Leverage::get()->pluck('leverage');
        $times = Time::get()->pluck('time');
        return view('new_order', compact('parities', 'leverages', 'times'));
    }

    public function orderSave(Request $request)
    {
        $parities = Parity::get()->pluck('parity');
        $leverages = Leverage::get()->pluck('leverage');
        $times = Time::get()->pluck('time');
        $validator = validator()->make(request()->all(), [
            'leverage' => 'required|filled|integer|in:' . implode(",", $leverages->toArray()),
            'time' => 'required|filled|string|in:' . implode(",", $times->toArray()),
            'percent' => 'required|filled|integer|in:' . implode(",", config('order.percent')),
            'parity' => 'required|filled|string|in:' . implode(",", $parities->toArray())
        ]);
        if ($validator->fails()) {
            return redirect()->back();
        }
        $parity = Parity::where('parity', $request->parity)->first();
        $leverage = Leverage::where('leverage', $request->leverage)->first();
        $time = Time::where('time', $request->time)->first();
        $user = User::where('login_key', $this->user)->first();
        Order::create([
            'users_id' => $user->id,
            'parities_id' => $parity->id,
            'leverages_id' => $leverage->id,
            'times_id' => $time->id,
            'percent' => $request->percent,
        ]);
        return redirect()->route('panel.dashboard');
    }
}
