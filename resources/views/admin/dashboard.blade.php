@extends('layout.app')
@section('container')

            <div class="col-12 col-md-6">
                <div class="col-12 text-center m-2">
                    <a href="{{ route('panel.admin.users') }}" title="Üyeler" class="btn btn-outline-warning mt-5">Üyeler</a>
                    <a href="{{ route('panel.admin.times') }}" title="Zaman Ayarları" class="btn btn-outline-warning mt-5">Zaman Ayarları</a>
                </div>
            </div>
@endsection
