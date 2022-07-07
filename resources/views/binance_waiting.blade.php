@extends('layout.app')
@section('container')
    @if((!$user->api_status) && count($user->api_permissions)==0)
        <div class="col-12 col-md-6">
            <div class="row">
                <div class="col-12 text-center">
                    <h1><i class="bi bi-bag-check"></i></h1>
                </div>
                <div class="col-12 text-center m-2">
                    <div class="btn-shine"></div>
                    <div class="copright" data-text="{{ __('app.permissions_check') }}">{{ __('app.permissions_check') }}</div>
                    <div>{{ __('app.auto_refresh_page') }}</div>
                </div>
            </div>
        </div>
    @elseif((!$user->api_status) && count($user->api_permissions)>0)
        <div class="col-12 col-md-6">
            <div class="row">
                <div class="col-12 text-center">
                    <h1><i class="bi bi-bag-x"></i></h1>
                </div>
                <div class="col-12 text-center m-2">
                    <div class="btn-shine"></div>
                    <div class="copright" data-text="{{ __('app.insufficient_permission') }}">{{ __('app.insufficient_permission') }}</div>
                    <div class="mt-2">
                        <button type="button" class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#learnModal">{{ __('app.how_to_do') }}</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal fade" id="learnModal" tabindex="-1" aria-labelledby="learnModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-body text-center">
                        <img src="{{ asset('assets/learn/api-perms.gif') }}" style="min-width: 100%;width: 100%;">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{{ __('app.close') }}</button>
                        <a href="https://www.binance.com/en-GB/my/settings/api-management" target="_blank" class="btn btn-warning text-dark">{{ __('app.go_to_binance') }}</a>
                    </div>
                </div>
            </div>
        </div>
    @else
        <div class="col-12 col-md-6">
            <div class="row">
                <div class="col-12 text-center">
                    <h1><i class="bi bi-hourglass"></i></h1>
                </div>
                <div class="col-12 text-center m-2">
                    <div class="btn-shine"></div>
                    <div class="copright" data-text="{{ __('app.being_checked_title') }}">{{ __('app.being_checked_title') }}</div>
                    <div>{{ __('app.being_checked_desc') }}</div>
                </div>
            </div>
        </div>
    @endif
@endsection
