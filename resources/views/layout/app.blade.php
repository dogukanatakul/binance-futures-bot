@include('layout.header')
<div class="container">
    @if(Session::has('error'))
        <div class="alert alert-warning alert-dismissible fade show" style="position: fixed;top: 0;right: 0;" role="alert">
            <strong>{{ Session::get('error') }}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    @endif
    <div class="row justify-content-center align-items-center" style="min-height: 100vh">
        @yield('container')
    </div>
</div>
@include('layout.footer')
