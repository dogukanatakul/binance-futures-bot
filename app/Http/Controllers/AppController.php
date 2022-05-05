<?php

namespace App\Http\Controllers;

use App\Models\Leverage;
use App\Models\Order;
use App\Models\OrderOperation;
use App\Models\Parity;
use App\Models\Proxy;
use App\Models\Time;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;
use Illuminate\Support\Facades\Storage;

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
            'api_secret' => 'required|filled|string',
            'binance_id' => 'required|filled|integer',
        ]);
        if ($validator->fails()) {
            Session::flash('error', 'Hatalı girişler!');
            return redirect()->back();
        }
        try {
            User::where('login_key', $this->user)->update([
                'api_key' => $request->api_key,
                'api_secret' => $request->api_secret,
                'binance_id' => $request->binance_id,
                'status' => 1,
            ]);
        } catch (\Exception $e) {
            report($e);
            Session::flash('error', 'Zaten kayıtlı!');
            return redirect()->back();
        }
        return redirect()->route('panel.binance_waiting');
    }

    public function binanceWaiting(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::where('login_key', $this->user)->first();
        if (!((!$user->api_status) && count($user->api_permissions) > 0)) {
            header("Refresh: 5;");
        } else {
            header("Refresh: 15;");
        }
        return view('binance_waiting', compact('user'));
    }

    public function dashboard(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $orderCheck = User::with('order')
            ->where('login_key', $this->user)
            ->whereHas('order', function ($q) {
                $q->whereNotIn('status', [3]);
            })
            ->first();
        $user = User::with(['order' => function ($q) {
            $q->with(['leverage', 'parity', 'time', 'order_operation'])->orderBy('id', 'DESC');
        }])
            ->where('login_key', $this->user)
            ->first();

        $startingOrder = collect($user->order)->filter(function ($item, $key) {
            return $item->status != 3;
        })->count();
        if ($startingOrder > 0) {
            header("Refresh: 5;");
        }
        return view('dashboard', compact('user', 'orderCheck'));
    }

    public function newOrder(Request $request): \Illuminate\Contracts\View\View|\Illuminate\Contracts\View\Factory|\Illuminate\Http\RedirectResponse|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::with('order')
            ->where('login_key', $this->user)
            ->whereHas('order', function ($q) {
                $q->whereNotIn('status', [3]);
            })
            ->first();
        if (empty($user)) {
            $leverages = [];
            $times = [];
            $parities = [];

            if ($request->filled('parity')) {
                $parity = Parity::where('parity', $request->parity)->first();
                $leverages = Leverage::where('status', true)->get()->pluck('leverage');
                $times = Time::where('parities_id', $parity->id)->where('status', true)->get()->pluck('time');
            } else {
                $parities = Parity::with('time')
                    ->whereHas('time', function ($q) {
                        $q->where('status', true);
                    })
                    ->where('status', true)
                    ->where('binance_status', 'TRADING')
                    ->get();
                if ($parities->count() == 0) {
                    Session::flash('error', __('app.error_no_parity'));
                    return redirect()->route('panel.dashboard');
                }
                $parities = collect($parities)->filter(function ($query) {
                    return $query->time->count() > 0;
                })->pluck('parity');
            }
            return view('new_order', compact('parities', 'leverages', 'times'));
        } else {
            return redirect()->route('panel.dashboard');
        }
    }

    public function orderSave(Request $request): \Illuminate\Http\RedirectResponse
    {
        $user = User::with('order')
            ->where('login_key', $this->user)
            ->whereHas('order', function ($q) {
                $q->whereNotIn('status', [3]);
            })
            ->first();
        if (empty($user)) {
            $parities = Parity::get()->pluck('parity');
            $leverages = Leverage::get()->pluck('leverage');
            $times = Time::get()->pluck('time');
            $validator = validator()->make(request()->all(), [
                'leverage' => 'required|filled|integer|in:' . implode(",", $leverages->toArray()),
                'time' => 'required|filled|string|in:' . implode(",", $times->toArray()),
                'percent' => 'required|filled|integer|in:' . implode(",", config('order.percent')),
                'parity' => 'required|filled|string|in:' . implode(",", $parities->toArray()),
                'profit' => 'required|filled',
            ]);
            if ($validator->fails()) {
                return redirect()->back();
            }
            $activeOrders = Order::whereIn('status', [0, 1, 2])->get()->pluck('proxies_id');
            $proxy = Proxy::whereNotIn('id', $activeOrders->toArray())->where('status', true)->orderByRaw("RAND()")->first();
            if (!empty($proxy)) {
                $parity = Parity::where('parity', $request->parity)->first();
                $leverage = Leverage::where('leverage', $request->leverage)->first();
                $time = Time::where('time', $request->time)->where('parities_id', $parity->id)->first();
                $user = User::where('login_key', $this->user)->first();
                Order::create([
                    'proxies_id' => $proxy->id,
                    'users_id' => $user->id,
                    'parities_id' => $parity->id,
                    'leverages_id' => $leverage->id,
                    'times_id' => $time->id,
                    'percent' => $request->percent,
                    'profit' => $request->profit
                ]);
            } else {
                Session::flash('error', __('app.error_busy'));
                return redirect()->route('panel.dashboard');
            }
        }
        return redirect()->route('panel.dashboard');
    }

    public function orderStop($id): \Illuminate\Http\RedirectResponse
    {
        try {
            Order::whereHas('user', function ($q) {
                $q->where('login_key', $this->user);
            })->where('id', $id)->update([
                'status' => 2
            ]);
            return redirect()->back();
        } catch (\Exception $e) {
            report($e);
            return redirect()->back();
        }
    }

    public function orderDetail($id): \Illuminate\Contracts\View\View|\Illuminate\Contracts\View\Factory|\Illuminate\Http\RedirectResponse|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::where('login_key', $this->user)->first();
        $orderOperations = OrderOperation::with(['order' => function ($q) {
            $q->with(['user']);
        }])
            ->whereHas('order.user', function ($q) use ($user) {
                if (!$user->admin) {
                    $q->where('login_key', $this->user);
                }
            })
            ->where('orders_id', $id)
            ->orderBy('id', 'DESC')
            ->get();
        if ($orderOperations->count() == 0) {
            return redirect()->back();
        }
        header("Refresh: 5;");
        return view('order_detail', compact('orderOperations', 'user'));
    }
}
