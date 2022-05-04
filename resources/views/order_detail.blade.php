@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh;">
            <div class="col-12">
                <div class="row">
                    <div class="col-12">
                        <div class="d-grid gap-2">
                            <a href="{{ $user->admin ? route('panel.admin.orders'): route('panel.dashboard') }}" class="btn btn-outline-warning btn-sm">{{ __('app.go_back') }}</a>
                        </div>
                    </div>
                    <div class="col-12" style="max-width: 100%;max-height:40vh;overflow-x:auto;overflow-y: auto">
                        <table class="table table-striped table-dark">
                            <thead>
                            <tr>
                                <th scope="col">{{ __('app.order_detail_price') }}</th>
                                <th scope="col">{{ __('app.order_detail_amount') }}</th>
                                <th scope="col">{{ __('app.order_detail_balance') }}</th>
                                <th scope="col">{{ __('app.order_detail_profit') }}</th>
                                <th scope="col">{{ __('app.order_detail_side') }}</th>
                                <th scope="col">{{ __('app.order_detail_position') }}</th>
                                <th scope="col">{{ __('app.order_detail_action') }}</th>
                                @if($user->admin)
                                    <th scope="col">K</th>
                                    <th scope="col">D</th>
                                    <th scope="col">J</th>
                                    <th scope="col">{{ __('app.order_detail_time') }}</th>
                                @endif
                            </tr>
                            </thead>
                            <tbody>
                            @foreach($orderOperations as $operation)
                                <tr>
                                    <td>
                                        {{ $operation->price }}
                                    </td>
                                    <td>
                                        {{ $operation->balance }}
                                    </td>
                                    <td>
                                        {{ $operation->quantity }}
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
                                    @if($user->admin)
                                        <td>
                                            {{ $operation->K }}
                                        </td>
                                        <td>
                                            {{ $operation->D }}
                                        </td>
                                        <td>
                                            {{ $operation->J }}
                                        </td>
                                        <td>
                                            {{ $operation->time }}
                                        </td>
                                    @endif
                                </tr>
                            @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
@endsection
