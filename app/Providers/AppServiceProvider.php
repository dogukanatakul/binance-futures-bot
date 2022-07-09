<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Queue\Events\JobFailed;
use Illuminate\Queue\Events\JobProcessed;
use Illuminate\Support\Facades\Queue;
use Symfony\Component\HttpFoundation\Request;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     *
     * @return void
     */
    public function register()
    {
        //
    }

    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {
        Request::setTrustedProxies(['REMOTE_ADDR'], Request::HEADER_X_FORWARDED_FOR);

        Queue::after(function (JobProcessed $event) {
            $this->retry($event);
        });

        Queue::failing(function (JobFailed $event) {
            $this->retry($event, true);
        });
    }

    public function retry($event, $fail = false)
    {
        $jobName = $event->job->payload()['data']['commandName'];
        if ($jobName === 'App\Jobs\BotSetOrder') {
            \App\Jobs\BotSetOrder::dispatch()->onQueue('bot')->delay(now()->tz('Europe/Istanbul')->addSeconds(2));
        }
    }

}
