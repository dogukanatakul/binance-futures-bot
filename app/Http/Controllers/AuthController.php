<?php

namespace App\Http\Controllers;

use App\Contracts\AuthRepository;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;


class AuthController extends Controller
{
    protected $contract;

    public function __construct(AuthRepository $contract)
    {
        $this->contract = $contract;
    }


    public function register(): \Illuminate\Http\JsonResponse
    {
        $credentials = request([
            'name',
            'email',
            'password'
        ]);

        $rules = [
            'name' => 'required|max:255',
            'email' => 'required|email|max:255|unique:users'
        ];

        $validator = Validator::make($credentials, $rules);
        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'error' => $validator->messages()
            ], 401);
        }
        $this->contract->create($credentials);
        return response()->json([
            'success' => true,
            'data' => [
                'message' => 'Thanks for signing up! Please check your e-mail to complete your registration.'
            ]
        ]);
    }

    public function login(): \Illuminate\Http\JsonResponse
    {
        $credentials = request(['email', 'password']);
        $rules = [
            'email' => 'required|email',
            'password' => 'required'
        ];
        $validator = Validator::make($credentials, $rules);
        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'error' => $validator->messages()
            ], 401);
        }
        $credentials['confirmation_code'] = NULL;
        try {
            if (!$token = auth('api')->attempt($credentials)) {
                return response()->json([
                    'success' => false,
                    'error' => 'Invalid credentials or E-Mail verification is pending'
                ], 401);
            }

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Invalid credentials, please try again'
            ], 500);
        }
        return response()->json([
            'success' => true,
            'data' => [
                'token' => $token,
                'expires_in' => auth('api')->factory()->getTTL() * 60
            ]
        ]);
    }
}
