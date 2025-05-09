@extends('layout.app')
@section('container')
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
            <div class="col-12 mb-2 justify-content-center align-items-center text-center">
                <a target="_blank" href="https://accounts.binance.com/tr/register?ref={{ $user->reference->code }}" class="btn btn-outline-secondary btn-xs">{{ __('app.register_reference_button') }}</a>
            </div>
            <div class="col-12">
                <form method="POST" action="{{ route("panel.binance_save") }}" class="card bg-dark">
                    @csrf
                    <div class="card-body">
                        <div class="input-group input-group-lg mb-2">
                            <input type="password" name="binance_id" class="form-control text-center bg-dark text-light" placeholder="Binance ID">
                        </div>
                        <div class="input-group input-group-lg mb-2">
                            <input type="password" name="api_key" class="form-control text-center bg-dark text-light" placeholder="{{ __('app.api_key') }}">
                        </div>
                        <div class="input-group input-group-lg mb-2">
                            <input type="password" name="api_secret" class="form-control text-center bg-dark text-light" placeholder="{{ __('app.api_secret') }}">
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-outline-warning btn-lg">{{ __('app.save') }}</button>
                        </div>
                        <div class="d-grid gap-2 mt-2">
                            <button type="button" class="btn btn-outline-secondary btn-sm">{{ __('app.how_to_do') }}</button>
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
@endsection
