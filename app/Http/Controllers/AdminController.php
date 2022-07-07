<?php

namespace App\Http\Controllers;

use App\Models\Leverage;
use App\Models\Order;
use App\Models\Parity;
use App\Models\Time;
use App\Models\TimeIndicatorPeriod;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;
use Illuminate\Support\Facades\Storage;

class AdminController extends Controller
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

    public function dashboard(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        return view('admin.dashboard');
    }

    public function users(Request $request): \Illuminate\Contracts\View\View|\Illuminate\Contracts\View\Factory|\Illuminate\Http\RedirectResponse|\Illuminate\Contracts\Foundation\Application
    {
        if ($request->filled('admin')) {
            $userUpdate = User::where('id', $request->admin)->first();
            $userUpdate->admin = !$userUpdate->admin;
            $userUpdate->save();
            return redirect()->back();
        }
        if ($request->filled('confirmation')) {
            $userUpdate = User::where('id', $request->confirmation)->first();
            $userUpdate->status = 2;
            $userUpdate->save();
            return redirect()->back();
        }
        $users = User::withoutTrashed()->whereIn('status', [1, 2])->where('api_status', true)->orderBy('status', 'ASC')->get();
        return view('admin.users', compact('users'));
    }


    public function times(Request $request): \Illuminate\Contracts\View\View|\Illuminate\Contracts\View\Factory|\Illuminate\Http\RedirectResponse|\Illuminate\Contracts\Foundation\Application
    {
        $forbidden = in_array((int)now('Europe/Istanbul')->format('i'), [
            00,
            13,
            14,
            15,
            28,
            29,
            30,
            43,
            44,
            45,
            58,
            59,
        ]);
        if ($request->filled('status')) {
            $parity = Parity::where('id', $request->status)->first();
            $parity->status = !$parity->status;
            $parity->save();
            return redirect()->back();
        }
        $parities = Parity::orderBy('parity', 'ASC')->get();
        $times = [];
        $selectTimes = [];
        if ($request->filled('parity')) {
            $times = Time::with('parity')->where('parities_id', $request->parity)->get();
            $selectTimes = collect($times)->mapWithKeys(function ($item) {
                return [$item['id'] => $item['time']];
            });
        }
        return view('admin.times', compact('times', 'parities', 'selectTimes', 'forbidden'));
    }

    public function timeSave(Request $request): \Illuminate\Http\RedirectResponse
    {
        $validator = validator()->make(request()->all(), [
            'id' => 'required|filled|integer',
            'update.MAX_DAMAGE_USDT_PERCENT' => 'required|filled|numeric',
            'update.BRS_M' => 'required|filled|numeric',
            'update.BRS_T' => 'required|filled|numeric',
            'update.BRS_LIMIT' => 'required|filled|integer|min:1',
        ]);
        if ($validator->fails()) {
            Session::flash('error', 'Hatalı girişler!');
            return redirect()->back();
        }
        $update = $request->update;
        if (!$request->filled('update.status')) {
            $update['status'] = 0;
        }
        if (Time::where('id', $request->id)->first()->export_time == 0) {
            $update['export_time'] = (int)(microtime(true) * 1000.0);
        }
        $forbidden = in_array((int)now('Europe/Istanbul')->format('i'), [
            00,
            13,
            14,
            15,
            28,
            29,
            30,
            43,
            44,
            45,
            58,
            59,
        ]);
        if ($forbidden) {
            unset($update['BRS_M']);
            unset($update['BRS_T']);
            Session::flash('error', 'Değerler değişmedi! Yasaklı zaman dilimi içerisinde güncelleme yapmaya çalıştınız.');
        }
        $update['export_time_status'] = true;
        Time::where('id', $request->id)->update($update);
        return redirect()->back();
    }


    public function export(Request $request): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $parities = Parity::orderBy('parity', 'ASC')->get();
        $times = [];
        $selectTimes = [];
        if ($request->filled('parity')) {
            $times = Time::with('parity')->where('parities_id', $request->parity)->get();
            $selectTimes = collect($times)->mapWithKeys(function ($item) {
                return [$item['id'] => $item['time']];
            });
            header("Refresh: 5;");
        }
        $status = [
            'Bekliyor',
            'Hazırlanıyor',
            'Hazır'
        ];
        return view('admin.export', compact('times', 'parities', 'selectTimes', 'status'));
    }

    public function exportUpdate($id): \Illuminate\Http\RedirectResponse
    {
        Time::where('id', $id)->update([
            'export' => 1
        ]);
        return redirect()->back();
    }

    public function exportInfo($id)
    {
        $infos = TimeIndicatorPeriod::where('times_id', $id)->orderBy('microtime', 'DESC')->get();
        header("Refresh: 5;");
        return view('admin.export_info', compact('infos', 'id'));
    }

    public function orders(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $user = User::where('login_key', $this->user)->first();
        $orders = Order::with('user', 'order_operation')->orderBy('status', 'ASC')->orderBy('id', 'DESC')->get();
        header("Refresh: 5;");
        return view('admin.orders', compact('orders', 'user'));
    }

    public function leverages(Request $request): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        if ($request->filled('status')) {
            $leverage = Leverage::where('id', $request->status)->first();
            $leverage->status = !$leverage->status;
            $leverage->save();
        }
        $leverages = Leverage::get();
        return view('admin.leverages', compact('leverages'));
    }

}
