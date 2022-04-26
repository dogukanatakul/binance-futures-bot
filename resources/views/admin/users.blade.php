@extends('layout.app')
@section('container')
    <div class="col-12">
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
                        <th scope="col">E-Posta</th>
                        <th scope="col">Binance ID</th>
                        <th scope="col">Durum</th>
                        <th scope="col">Kayıt Tarihi</th>
                    </tr>
                    </thead>
                    <tbody>
                    @foreach($users as $user)
                        <tr>
                            <td>
                                {{ $user->email }}
                            </td>
                            <td>
                                {{ $user->binance_id }}
                            </td>
                            <td class="text-end">
                                @if($user->status==1)
                                    <a href="{{ route('panel.admin.users')."?confirmation=".$user->id }}" class="btn btn-outline-secondary btn-sm">Onayla</a>
                                @else
                                    <a href="{{ route('panel.admin.users')."?admin=".$user->id }}" class="btn btn-outline-secondary btn-sm">{{ $user->admin?'Admin':'Üye' }}</a>
                                @endif
                            </td>
                            <td>
                                {{ $user->created_at->format('y-m-d H:i') }}
                            </td>
                        </tr>
                    @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>
@endsection
