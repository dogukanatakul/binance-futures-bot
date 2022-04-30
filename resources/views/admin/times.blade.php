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
                            <th scope="col">Başlama Farkı%</th>
                            <th scope="col">Sahte Ters İşlem</th>
                            <th scope="col">Tetikleme %'si</th>
                            <th scope="col">Başlangıçta minimum SHORT işlem sayısı</th>
                            <th scope="col">İşlem terse dönerse kaç işlem beklesin</th>
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
                                            <input type="number" class="form-control" name="update[start_diff]" value="{{ $time->start_diff }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[fake_reverse]" value="{{ $time->fake_reverse }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[trigger_diff]" value="{{ $time->trigger_diff }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[start_trigger_min]" value="{{ $time->start_trigger_min }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[reverse_delay]" value="{{ $time->reverse_delay }}">
                                        </div>
                                    </td>
                                    <td>
                                        <button type="submit" onclick="return confirm('Abdurrahim Albayrak söylemiyle FAZİYAA ya yol açabilir! Emin misin?')" class="btn btn-outline-warning btn-sm"><i class="bi bi-arrow-clockwise"></i></button>
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
