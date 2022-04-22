<?php

namespace App\Contracts;

interface AuthRepository
{

    public function create($credentials): \App\Models\User;

    public function update($user, $credentials): \App\Models\User;

}
