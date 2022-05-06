@extends('layout.app')
@section('container')

    <div class="col-12 col-md-6">
        @if(request()->filled('parity'))
            <form method="POST" action="{{ route('panel.order_save') }}" class="row justify-content-center align-items-center">
                @csrf
                <input type="hidden" name="parity" value="{{ request()->parity }}">
                <div class="col-12  text-center mt-2">
                    <h6>{{ __('app.order_leverage') }}</h6>
                    <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                        @foreach($leverages as $leverage)
                            <input type="radio" value="{{ $leverage }}" class="btn-check" name="leverage" id="leverage{{ $leverage }}" autocomplete="off" {{ $leverage==10?'checked':'' }}>
                            <label class="btn btn-outline-warning" for="leverage{{ $leverage }}">{{ $leverage }}x</label>
                        @endforeach
                    </div>
                </div>
                <div class="col-12 mt-2 text-center">
                    <h6>{{ __('app.order_amount') }}</h6>
                    <div class="btn-group btn-group-justified" role="group" aria-label="Basic radio toggle button group">
                        @foreach(config('order.percent') as $percent)
                            <input type="radio" value="{{ $percent }}" class="btn-check" name="percent" id="percent{{ $percent }}" autocomplete="off" {{ $percent==10?'checked':'' }}>
                            <label class="btn btn-outline-warning btn-lg" for="percent{{ $percent }}">{{ $percent }}%</label>
                        @endforeach
                    </div>
                </div>
                <div class="col-12 mt-2 text-center">
                    <h6>{{ __('app.order_time') }}</h6>
                    <div class="btn-group btn-group-justified" role="group" aria-label="Basic radio toggle button group">
                        @if($i=0)@endif
                        @foreach($times as $time)
                            <input type="radio" value="{{ $time }}" class="btn-check" name="time" id="time{{ $time }}" autocomplete="off" {{ $i==0?'checked':'' }}>
                            <label class="btn btn-outline-warning btn-lg" for="time{{ $time }}">{{ $time }}</label>
                            @if($i++)@endif
                        @endforeach
                    </div>
                </div>
                <div class="col-12 mt-2 text-center">
                    <h6>{{ __('app.order_profit') }}</h6>
                    @foreach(range(0, 30, 20) as $profit)
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="profit" id="inlineRadio{{ $profit }}" value="{{ $profit }}" {{ $profit==0?'checked':'' }}>
                            <label class="form-check-label text-warning" for="inlineRadio{{ $profit }}">{{ $profit==0?__('app.passive'):$profit.'%' }}</label>
                        </div>
                    @endforeach
                    @foreach(range(60, 100, 15) as $profit)
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="profit" id="inlineRadio{{ $profit }}" value="{{ $profit }}" {{ $profit==0?'checked':'' }}>
                            <label class="form-check-label text-warning" for="inlineRadio{{ $profit }}">{{ $profit==0?__('app.passive'):$profit.'%' }}</label>
                        </div>
                    @endforeach
                    @foreach(range(150, 200, 50) as $profit)
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="profit" id="inlineRadio{{ $profit }}" value="{{ $profit }}" {{ $profit==0?'checked':'' }}>
                            <label class="form-check-label text-warning" for="inlineRadio{{ $profit }}">{{ $profit==0?__('app.passive'):$profit.'%' }}</label>
                        </div>
                    @endforeach
                </div>
                <div class="col-12 mt-2">
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-outline-warning btn-lg">{{ __('app.create_order') }}</button>
                    </div>
                </div>
                <div class="col-12 mt-2">
                    <div class="d-grid gap-2">
                        <a href="{{ route('panel.dashboard') }}" class="btn btn-outline-info btn-sm">{{ __('app.go_back') }}</a>
                    </div>
                </div>
            </form>
        @else
            <form method="GET" action="{{ route('panel.new_order') }}" class="row justify-content-center align-items-center">
                <div class="col-12 mt-3">
                    <select class="form-select" name="parity">
                        @foreach($parities as $parity)
                            <option value="{{ $parity }}">{{ $parity }}</option>
                        @endforeach
                    </select>
                </div>
                <div class="col-12 mt-2">
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-outline-warning btn-lg">{{ __('app.select_parity') }}</button>
                    </div>
                </div>
            </form>
        @endif
    </div>
@endsection
