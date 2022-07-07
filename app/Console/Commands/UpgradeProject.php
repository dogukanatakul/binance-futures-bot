<?php

namespace App\Console\Commands;

use App\Models\Bot;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;

class UpgradeProject extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'upgrade:project';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Project Upgrade';

    /**
     * Execute the console command.
     *
     * @return int
     */
    public function handle(): int
    {
        DB::table('jobs')->truncate();
        DB::table('failed_jobs')->truncate();
        if (Bot::where('status', true)->get()->count() > 0) {
            Bot::where('status', false)->delete();
        } else {
            DB::table('bots')->truncate();
        }
        Artisan::call('queue:flush');
        Artisan::call('queue:restart');
        Artisan::call('queue:clear', [
            '--force' => true,
        ]);
        Artisan::call('cache:clear');
        Artisan::call('config:clear');
        Artisan::call('route:clear');
        \App\Jobs\BotSetOrder::dispatch()->onQueue('bot');
        return Command::SUCCESS;
    }
}
