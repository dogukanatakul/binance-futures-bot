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

    public int $timeout = 300;
    protected string $email;
    protected string $language;

    public function __construct($email, $language)
    {
        $this->email = $email;
        $this->language = $language;
    }

    /**
     * Execute the job.
     *
     * @return bool
     */
    public function handle(): bool
    {
        app()->setLocale($this->language);
        $user = User::withoutTrashed()->where('email', $this->email);
        if (empty($user->first())) {
            return false;
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
            $message->subject(config('app.name') . " - " . __('app.mail_title'));
        });
        return true;
    }
}
