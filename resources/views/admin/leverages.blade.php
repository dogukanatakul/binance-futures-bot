@extends('layout.app')
@section('container')
    <div class="col-6">
        <div class="row">
            <div class="col-12">
                <div class="d-grid gap-2">
                    <a href="{{ route('panel.admin.dashboard') }}" class="btn btn-outline-warning btn-sm">Geri Dön</a>
                </div>
            </div>
            <div class="col-12" style="max-width: 100%;max-height:40vh;overflow-x:auto;overflow-y: auto">
                <table class="table table-striped table-dark">
                    <thead>
                    <tr>
                        <th scope="col">Kaldıraç</th>
                        <th scope="col">Risk</th>
                        <th scope="col" class="text-end">Durum</th>
                    </tr>
                    </thead>
                    <tbody>
                    @foreach($leverages as $leverage)
                        <tr>
                            <td>
                                {{ $leverage->leverage }}x
                            </td>
                            <td>
                                {{ $leverage->risk_percentage }}%
                            </td>
                            <td class="text-end">
                                <a href="{{ route('panel.admin.leverages')."?status=".$leverage->id }}" class="btn btn-outline-secondary btn-sm">{{ $leverage->status?'Aktifliği Kaldır':'Aktif Yap' }}</a>
                            </td>
                        </tr>
                    @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>
@endsection
