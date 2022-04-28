<?php

namespace App\Http\Controllers;

use App\Models\Order;
use App\Models\Parity;
use App\Models\Time;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class AdminController extends Controller
{
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


    public function times(Request $request): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $parities = Parity::get();
        $times = [];
        if ($request->filled('parity')) {
            $times = Time::with('parity')->where('parities_id', $request->parity)->get();
        }
        return view('admin.times', compact('times', 'parities'));
    }

    public function timeSave(Request $request): \Illuminate\Http\RedirectResponse
    {
        $validator = validator()->make(request()->all(), [
            'id' => 'required|filled|integer',
            'update.start_diff' => 'required|filled|integer',
            'update.fake_reverse' => 'required|filled|integer',
            'update.trigger_diff' => 'required|filled|integer',
            'update.short_trigger_min' => 'required|filled|integer',
            'update.reverse_delay' => 'required|filled|integer',
        ]);
        if ($validator->fails()) {
            Session::flash('error', 'Hatalı girişler!');
            return redirect()->back();
        }
        Time::where('id', $request->id)->update($request->update);
        return redirect()->back();
    }

    public function orders(): \Illuminate\Contracts\View\Factory|\Illuminate\Contracts\View\View|\Illuminate\Contracts\Foundation\Application
    {
        $orders = Order::with('user')->get();
        header("Refresh: 5;");
        return view('admin.orders', compact('orders'));
    }

}
