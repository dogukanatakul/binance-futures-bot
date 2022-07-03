@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh;">
            <div class="col-12">
                <div class="row">
                    <div class="col-12">
                        <div class="d-grid gap-2">
                            <a href="{{ route('panel.admin.export')."?parity=".$id }}" class="btn btn-outline-warning btn-sm">{{ __('app.go_back') }}</a>
                        </div>
                    </div>
                    <div class="col-12" style="max-width: 100%;max-height:50vh;overflow-x:auto;overflow-y: auto">
                        <table class="table table-striped table-dark">
                            <thead>
                            <tr>
                                <th scope="col">Tarih</th>
                                <th scope="col">Açılış</th>
                                <th scope="col">Kapanış</th>
                                <th scope="col">Yüksek</th>
                                <th scope="col">Düşük</th>
                                <th scope="col">M</th>
                                <th scope="col">T</th>
                                <th scope="col">C</th>
                                <th scope="col">BRS</th>
                                <th scope="col">Yön</th>
                            </tr>
                            </thead>
                            <tbody>
                            @foreach($infos as $info)
                                <tr>
                                    <td>
                                        {{ $info->values['dateFormat'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['Open'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['Close'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['High'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['Low'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['M'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['T'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['C'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['BRS'] ?? '' }}
                                    </td>
                                    <td>
                                        {{ $info->values['type'] ?? '' }}
                                    </td>
                                </tr>
                            @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
@endsection
