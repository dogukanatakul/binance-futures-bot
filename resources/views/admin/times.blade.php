@extends('layout.app')
@section('container')
    <div class="{{ request()->filled('parity')?'col-12':'col-12 col-md-6' }}">
        <div class="row">
            <div class="col-12">
                <div class="d-grid gap-2">
                    @if(request()->filled('parity'))
                        <a href="{{ route('panel.admin.times') }}" class="btn btn-outline-warning btn-sm">Geri Dön</a>
                    @else
                        <a href="{{ route('panel.admin.dashboard') }}" class="btn btn-outline-warning btn-sm">Geri Dön</a>
                    @endif
                </div>
            </div>
            @if(!request()->filled('parity'))
                <div class="col-12" style="max-width: 100%;max-height:40vh;overflow-x:auto;overflow-y: auto">
                    <table class="table table-striped table-dark">
                        <thead>
                        <tr>
                            <th scope="col">Parite</th>
                            <th scope="col">Seçim</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($parities as $parity)
                            <tr>
                                <td class="text-center">
                                    {{ $parity->parity }}
                                </td>
                                <td>
                                    <div class="d-grid gap-2">
                                        <a href="{{ route('panel.admin.times')."?parity=".$parity->id }}" class="btn btn-outline-warning btn-sm">Seç</a>
                                    </div>
                                </td>
                            </tr>
                        @endforeach
                        </tbody>
                    </table>
                </div>
            @else
                <div class="col-12" style="max-width: 100%;max-height:60vh;overflow-x:auto;overflow-y: auto">
                    <table class="table table-striped table-dark">
                        <thead>
                        <tr>
                            <th scope="col">Zaman</th>
                            <th scope="col">KDJ Period</th>
                            <th scope="col">KDJ Signal</th>

                            <th scope="col">ATR Period</th>
                            <th scope="col">ATR Multiplier</th>


                            <th scope="col">MACD Short</th>
                            <th scope="col">MACD Long</th>
                            <th scope="col">MACD Signal</th>

                            <th scope="col">Durum</th>
                            <th scope="col"><i class="bi bi-arrow-clockwise"></i></th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($times as $time)
                            <form method="POST" action="{{ route('panel.admin.time_save') }}">
                                @csrf
                                <input type="hidden" name="id" value="{{ $time->id }}">
                                <tr>
                                    <td class="text-center">
                                        {{ $time->time }}
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[kdj_period]" value="{{ $time->kdj_period }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[kdj_signal]" value="{{ $time->kdj_signal }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[atr_period]" value="{{ $time->atr_period }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" min="0" step="0.1" name="update[atr_multiplier]" value="{{ $time->atr_multiplier }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[dema_short]" value="{{ $time->dema_short }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[dema_long]" value="{{ $time->dema_long }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[dema_signal]" value="{{ $time->dema_signal }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="form-check form-switch">
                                            <input class="form-check-input" type="checkbox" name="update[status]" id="flexSwitchCheckChecked" value="1" {{ $time->status ? 'checked':'' }}>
                                        </div>
                                    </td>
                                    <td>
                                        <button type="submit" onclick="return confirm('OK?')" class="btn btn-outline-warning btn-sm"><i class="bi bi-arrow-clockwise"></i></button>
                                    </td>
                                </tr>
                            </form>
                        @endforeach
                        </tbody>
                    </table>
                </div>
            @endif

        </div>
    </div>
@endsection
