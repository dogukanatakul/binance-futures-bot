@extends('layout.app')
@section('container')
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh">
            <div class="col-12 col-md-8">
                <div class="row">
                    <div class="col-12 text-center">
                        <h1><i class="bi bi-envelope-paper-heart"></i></h1>
                        <h4>{{ __('auth.check_mail_title') }}</h4>
                        <p>{{ __('auth.check_mail_warning') }}</p>
                        <a href="mailto:" class="btn btn-outline-secondary btn-sm">{{ __('auth.go_mail_app') }}</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection
