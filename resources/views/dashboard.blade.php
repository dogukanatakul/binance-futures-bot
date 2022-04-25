@extends('layout.app')
@section('container')
    @if($user->order->count()==0)
        <div class="col-12 col-md-6">
            <div class="row">
                <div class="col-12 text-center">
                    <h1><i class="bi bi-arrow-through-heart"></i></h1>
                </div>
                <div class="col-12 text-center m-2">
                    <div class="btn-shine"></div>
                    <div>Aramıza katılarak kalbimizi kazandınız.<br> Şimdi para kazanmak için ilk emrini oluştur!</div>
                    <a href="{{ route('panel.new_order') }}" title="Emir Oluştur" class="btn btn-outline-warning mt-5">Emir Oluştur</a>
                    @if($user->admin)
                        <a href="{{ route('panel.admin.dashboard') }}" title="Yönetim" class="btn btn-outline-info mt-5">Yönetim</a>
                    @endif
                </div>
            </div>
        </div>
    @else
        <div class="col-12 col-md-8">
            <div class="row">
                <div class="col-12">
                    <div class="d-grid gap-2">
                        @if(empty($orderCheck))
                            <a href="{{ route('panel.new_order') }}" class="btn btn-outline-warning btn-sm">Yeni Emir</a>
                        @else
                            <button type="button" class="btn btn-outline-warning btn-sm" disabled>Yeni Emir</button>
                        @endif
                        @if($user->admin)
                            <a href="{{ route('panel.admin.dashboard') }}" title="Yönetim" class="btn btn-outline-info btn-sm">Yönetim</a>
                        @endif
                    </div>
                </div>
                <div class="col-12" style="max-width: 100%;max-height:40vh;overflow-x:auto;overflow-y: auto">
                    <table class="table table-striped table-dark">
                        <thead>
                        <tr>
                            <th scope="col">Parite</th>
                            <th scope="col">Zaman</th>
                            <th scope="col">Kaldıraç</th>
                            <th scope="col">Başlama</th>
                            <th scope="col">Bitiş</th>
                            <th scope="col">İşlemler</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($user->order as $order)
                            <tr>
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
                                        <a href="{{ route('panel.order_stop', $order->id) }}" title="Durdur" class="btn btn-outline-danger btn-sm">Durdur</a>
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
    @endif
@endsection
