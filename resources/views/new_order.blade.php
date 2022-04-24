@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh">
            <div class="col-12 col-md-6">
                <form method="POST" action="{{ route('panel.order_save') }}" class="row justify-content-center align-items-center">
                    @csrf
                    <div class="col-12  text-center mt-2">
                        <h6>Kaldıraç:</h6>
                        <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                            @foreach($leverages as $leverage)
                                <input type="radio" value="{{ $leverage }}" class="btn-check" name="leverage" id="leverage{{ $leverage }}" autocomplete="off" {{ $leverage==10?'checked':'' }}>
                                <label class="btn btn-outline-warning" for="leverage{{ $leverage }}">{{ $leverage }}x</label>
                            @endforeach
                        </div>
                    </div>
                    <div class="col-12 mt-2 text-center">
                        <h6>Emir Miktarı:</h6>
                        <div class="btn-group btn-group-justified" role="group" aria-label="Basic radio toggle button group">
                            @foreach(config('order.percent') as $percent)
                                <input type="radio" value="{{ $percent }}" class="btn-check" name="percent" id="percent{{ $percent }}" autocomplete="off" {{ $percent==10?'checked':'' }}>
                                <label class="btn btn-outline-warning btn-lg" for="percent{{ $percent }}">{{ $percent }}%</label>
                            @endforeach
                        </div>
                    </div>
                    <div class="col-12 mt-2 text-center">
                        <h6>Zaman Aralığı:</h6>
                        <div class="btn-group btn-group-justified" role="group" aria-label="Basic radio toggle button group">
                            @foreach($times as $time)
                                <input type="radio" value="{{ $time }}" class="btn-check" name="time" id="time{{ $time }}" autocomplete="off" {{ $time=='5min'?'checked':'' }}>
                                <label class="btn btn-outline-warning btn-lg" for="time{{ $time }}">{{ $time }}</label>
                            @endforeach
                        </div>
                    </div>
                    <div class="col-12 mt-3">
                        <select class="form-select" name="parity">
                            @foreach($parities as $parity)
                                <option value="{{ $parity }}" {{ $parity=='ETHUSDT'?'selected':'' }}>{{ $parity }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div class="col-12 mt-2">
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-outline-warning btn-lg">Emir Oluştur</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
@endsection
