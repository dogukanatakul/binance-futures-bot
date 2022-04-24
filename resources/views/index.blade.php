@extends('layout.app')
@section('container')
<div class="container">
    <div class="row justify-content-center align-items-center" style="min-height: 100vh">
        <div class="col-12 col-md-6">
            <div class="row">
                <div class="col-12 text-center">
                    <div class="words">
                        <span>F</span>
                        <span>U</span>
                        <span>T</span>
                        <span>U</span>
                        <span>R</span>
                        <span>E</span>
                        <span>S</span>
                    </div>
                </div>
                <div class="col-12">
                    <form method="POST" action="{{ route("login") }}" class="card bg-dark">
                        @csrf
                        <div class="card-body">
                            <div class="input-group input-group-lg mb-2">
                                <input type="email" name="email" class="form-control text-center bg-dark text-light" placeholder="xxxx@xxxx.com">
                            </div>
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-outline-warning btn-lg">Giriş Bağlantısı Gönder</button>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="col-12 text-center m-2">
                    <div class="btn-shine"></div>
                    <div class="copright" data-text="Broovs Trade Bot v1.0 Alpha">Broovs Trade Bot v1.0 Alpha</div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
