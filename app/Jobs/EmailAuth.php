<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Support\Facades\Mail;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class EmailAuth implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $timeout = 300;
    protected $email;

    public function __construct($email)
    {
        $this->email = $email;
    }

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {

        $user = User::where('email', $this->email);
        if (empty($user->first())) {
            return;
        }
        $uuid = (string)\Illuminate\Support\Str::uuid();
        $user->update([
            'login_key' => $uuid,
        ]);

        $urls = [
            'login' => $uuid,
            'time' => now()->tz('Europe/Istanbul')->toDateTimeLocalString()
        ];

        Mail::send('email.login', ["url" => url("?" . http_build_query($urls))], function ($message) {
            $message->from(env('MAIL_FROM_ADDRESS'), config('app.name'));
            $message->to($this->email);
            $message->subject(config('app.name') . " - " . __('auth.mail_title'));
        });
    }
}
