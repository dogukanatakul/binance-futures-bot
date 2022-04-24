@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh">
            <div class="col-12 col-md-6">
                @if($user->order->count()==0)
                    <div class="row">
                        <div class="col-12 text-center">
                            <h1><i class="bi bi-arrow-through-heart"></i></h1>
                        </div>
                        <div class="col-12 text-center m-2">
                            <div class="btn-shine"></div>
                            <div>Aramıza katılarak kalbimizi kazandınız.<br> Şimdi para kazanmak için ilk emrini oluştur!</div>
                            <a href="{{ route('panel.new_order') }}" title="Emir Oluştur" class="btn btn-outline-warning mt-5">Emir Oluştur</a>
                        </div>
                    </div>
                @endif
            </div>
        </div>
    </div>
@endsection
