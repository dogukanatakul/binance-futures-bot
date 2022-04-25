@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh;">
            <div class="col-12">
                <div class="row">
                    <div class="col-12">
                        <div class="d-grid gap-2">
                            <a href="{{ url()->previous() }}" class="btn btn-outline-warning btn-sm">Geri Dön</a>
                        </div>
                    </div>
                    <div class="col-12" style="max-width: 100%;max-height:40vh;overflow-x:auto;overflow-y: auto">
                        <table class="table table-striped table-dark">
                            <thead>
                            <tr>
                                <th scope="col">Fiyat</th>
                                <th scope="col">Adet</th>
                                <th scope="col">Bakiye</th>
                                <th scope="col">Kâr</th>
                                <th scope="col">Taraf</th>
                                <th scope="col">Pozisyon</th>
                                <th scope="col">Aksiyon</th>
                                <th scope="col">K</th>
                                <th scope="col">D</th>
                                <th scope="col">J</th>
                            </tr>
                            </thead>
                            <tbody>
                            @foreach($orderOperations as $operation)
                                <tr>
                                    <td>
                                        {{ $operation->price }}
                                    </td>
                                    <td>
                                        {{ $operation->quantity }}
                                    </td>
                                    <td>
                                        {{ $operation->balance }}
                                    </td>
                                    <td>
                                        -
                                    </td>
                                    <td>
                                        {{ $operation->side }}
                                    </td>
                                    <td>
                                        {{ $operation->position_side }}
                                    </td>
                                    <td>
                                        {{ $operation->action }}
                                    </td>
                                    <td>
                                        {{ $operation->K }}
                                    </td>
                                    <td>
                                        {{ $operation->D }}
                                    </td>
                                    <td>
                                        {{ $operation->J }}
                                    </td>
                                </tr>
                            @endforeach
                            </tbody>
                        </table>
                    </div>

                </div>
            </div>

@endsection
