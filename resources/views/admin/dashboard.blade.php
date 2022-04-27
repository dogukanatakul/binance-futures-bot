@extends('layout.app')
@section('container')
    <div class="col-12 col-md-6">
        <div class="row">
            <div class="col-12 text-center">
                <div class="d-grid gap-2">
                    <a href="{{ route('panel.dashboard') }}" title="Üye Paneli" class="btn btn-outline-info mb-2">Üye Paneli</a>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-6 text-center">
                <div class="d-grid gap-2">
                    <a href="{{ route('panel.admin.users') }}" title="Üyeler" class="btn btn-outline-warning">Üyeler</a>
                </div>
            </div>
            <div class="col-6 text-center">
                <div class="d-grid gap-2">
                    <a href="{{ route('panel.admin.times') }}" title="Zaman Ayarları" class="btn btn-outline-warning">Zaman Ayarları</a>
                </div>
            </div>
            <div class="col-12 text-center mt-2">
                <div class="d-grid gap-2">
                    <a href="{{ route('panel.admin.orders') }}" title="Emirler" class="btn btn-outline-warning">Emirler</a>
                </div>
            </div>
        </div>

    </div>
@endsection
