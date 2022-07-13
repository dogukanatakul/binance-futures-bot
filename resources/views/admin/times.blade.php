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
                            <th scope="col" style="text-align: right">Aktif</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($parities as $parity)
                            <tr>
                                <td class="text-left">
                                    {{ $parity->parity }}
                                </td>
                                <td>
                                    <div class="d-grid gap-2">
                                        <a href="{{ route('panel.admin.times')."?parity=".$parity->id }}" class="btn btn-outline-warning btn-sm">Seç</a>
                                    </div>
                                </td>
                                <td class="text-end">
                                    <a href="{{ route('panel.admin.times')."?status=".$parity->id }}" class="btn btn-outline-secondary btn-sm">{{ $parity->status?'Aktifliği Kaldır':'Aktif Yap' }}</a>
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
                            <th scope="col">Max. Zarar</th>
                            <th scope="col">BRS_M</th>
                            <th scope="col">BRS_T</th>
                            <th scope="col">BRS_P1</th>
                            <th scope="col">BRS_P2</th>
                            <th scope="col">BRS_P3</th>
                            <th scope="col">BRS_P4</th>
                            <th scope="col">BRS_LIMIT</th>
                            <th scope="col">Durum</th>
                            <th scope="col"><i class="bi bi-arrow-clockwise"></i></th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($times as $time)
                            <form method="POST" action="{{ route('panel.admin.time_save') }}">
                                @csrf
                                <input type="hidden" name="id" value="{{ $time->id }}">
                                <input type="hidden" name="forbidden" value="{{ $forbidden }}">
                                <tr>
                                    <td class="text-center">
                                        {{ $time->time }}
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" name="update[MAX_DAMAGE_USDT_PERCENT]" min="0" step="0.0001" value="{{ $time->MAX_DAMAGE_USDT_PERCENT }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_M]" value="{{ $time->BRS_M }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_T]" value="{{ $time->BRS_T }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_P1]" value="{{ $time->BRS_P1 }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_P2]" value="{{ $time->BRS_P2 }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_P3]" value="{{ $time->BRS_P3 }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="text" class="form-control" {{ $forbidden ? 'disabled="disabled"':'' }} name="update[BRS_P4]" value="{{ $time->BRS_P4 }}">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="input-group input-group-sm">
                                            <input type="number" class="form-control" min="1" name="update[BRS_LIMIT]" value="{{ $time->BRS_LIMIT }}">
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
