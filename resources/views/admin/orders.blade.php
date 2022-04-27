@extends('layout.app')
@section('container')
    <div class="col-12 col-md-10">
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
                        <th scope="col">Kullanıcı</th>
                        <th scope="col">Parite</th>
                        <th scope="col">Zaman</th>
                        <th scope="col">Kaldıraç</th>
                        <th scope="col">Başlama</th>
                        <th scope="col">Bitiş</th>
                        <th scope="col">İşlemler</th>
                    </tr>
                    </thead>
                    <tbody>
                    @foreach($orders as $order)
                        <tr>
                            <td>
                                {{ explode("@",$order->user->email)[0] }}
                            </td>
                            <td>
                                {{ $order->parity->parity }}
                            </td>
                            <td>
                                {{ $order->time->time }}
                            </td>
                            <td>
                                {{ $order->leverage->leverage }}x
                            </td>
                            <td>
                                {{ $order->start->format('y-m-d H:i') }}
                            </td>
                            <td>
                                @if($order->status == 1 or $order->status == 0)
                                    Devam Ediyor.
                                @elseif($order->status == 2)
                                    Durmayı Bekliyor
                                @else
                                    {{ $order->finish->format('y-m-d H:i') }}
                                @endif
                            </td>
                            <td>
                                @if($order->order_operation->count()>0)
                                    <a href="{{ route('panel.order_detail', $order->id) }}" class="btn btn-outline-warning btn-sm"><i class="bi bi-ticket-detailed"></i></a>
                                @else
                                    <button type="button" class="btn btn-outline-warning btn-sm" disabled><i class="bi bi-ticket-detailed"></i></button>
                                @endif
                            </td>
                        </tr>
                    @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>
@endsection
