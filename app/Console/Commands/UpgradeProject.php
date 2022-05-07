<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

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
        \App\Jobs\BotSetOrder::dispatch()->onQueue('bot');
        return Command::SUCCESS;
    }
}
