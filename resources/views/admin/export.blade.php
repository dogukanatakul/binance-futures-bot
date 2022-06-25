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
                                        <a href="{{ route('panel.admin.export')."?parity=".$parity->id }}" class="btn btn-outline-warning btn-sm">Seç</a>
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
                            <th scope="col">Durum</th>
                            <th scope="col">İndir</th>
                            <th scope="col">Talep</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($times as $time)
                            <tr>
                                <td class="text-left">
                                    {{ $time->time }}
                                </td>
                                <td class="text-left">
                                    {{ $status[$time->export] }}
                                </td>
                                <td class="text-left">
                                    @if($time->export==0)
                                        Talep etmek için sağdaki butona tıklayın!
                                    @elseif($time->export==2)
                                        <a href="{{ url('export/'.$time->parity->parity."_".$time->time.".xlsx") }}">İndir</a>
                                    @else
                                        İşleniyor
                                    @endif
                                </td>

                                <td>
                                    <a href="{{ route('panel.admin.export_update', $time->id) }}" class="btn btn-outline-warning btn-sm"><i class="bi bi-arrow-clockwise"></i></a>
                                </td>
                            </tr>
                        @endforeach
                        </tbody>
                    </table>
                </div>
            @endif

        </div>
    </div>
@endsection
