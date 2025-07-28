'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  Phone, 
  ArrowLeft,
  Chrome,
  Facebook,
  Instagram,
  Apple
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { authAPI } from '@/lib/api';

type LoginMethod = 'email' | 'phone' | 'social';
type AuthStep = 'method' | 'credentials' | 'otp';

const LoginPage: React.FC = () => {
  const [loginMethod, setLoginMethod] = useState<LoginMethod>('email');
  const [authStep, setAuthStep] = useState<AuthStep>('method');
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    password: '',
    otp: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  
  const { login } = useAuth();
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleMethodSelect = (method: LoginMethod) => {
    setLoginMethod(method);
    if (method === 'social') {
      setAuthStep('method'); // Stay on method selection for social
    } else {
      setAuthStep('credentials');
    }
  };

  const handleSendOTP = async () => {
    setLoading(true);
    setError('');
    
    try {
      const contact = loginMethod === 'email' ? formData.email : formData.phone;
      const method = loginMethod === 'email' ? 'email' : 'sms';
      
      await authAPI.sendOTP(contact, method);
      setOtpSent(true);
      setAuthStep('otp');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const contact = loginMethod === 'email' ? formData.email : formData.phone;
      const method = loginMethod === 'email' ? 'email' : 'sms';
      
      const response = await authAPI.verifyOTP(contact, method, formData.otp);
      
      // Store token
      localStorage.setItem('token', response.access_token);
      
      router.push('/products');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'OTP verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData.email || formData.phone, formData.password);
      router.push('/products');
    } catch (error) {
      setError('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = async (provider: string) => {
    try {
      // In a real app, this would integrate with OAuth providers
      // For demo purposes, we'll simulate getting a token from the provider
      console.log(`Login with ${provider}`);
      
      // This would be replaced with actual OAuth flow
      // const token = await getOAuthToken(provider);
      // const response = await authAPI.socialAuth(provider, token);
      // localStorage.setItem('token', response.access_token);
      
      // For demo, redirect directly
      router.push('/products');
    } catch (error: any) {
      setError(`${provider} login failed. Please try again.`);
    }
  };

  const resetFlow = () => {
    setAuthStep('method');
    setLoginMethod('email');
    setFormData({ email: '', phone: '', password: '', otp: '' });
    setError('');
    setOtpSent(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Welcome back!</h2>
            <p className="mt-2 text-gray-600">Sign in to continue shopping</p>
          </div>

          {/* Back Button */}
          {authStep !== 'method' && (
            <button
              onClick={resetFlow}
              className="flex items-center text-blue-600 hover:text-blue-700 mb-6"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </button>
          )}

          {/* Method Selection */}
          {authStep === 'method' && (
            <div className="space-y-4">
              {/* Social Login Options */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose sign in method</h3>
                
                {/* Social Login Buttons */}
                <button
                  onClick={() => handleSocialLogin('google')}
                  className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
                >
                  <Chrome className="h-5 w-5 mr-3 text-red-500" />
                  <span className="text-gray-700 font-medium">Continue with Google</span>
                </button>

                <button
                  onClick={() => handleSocialLogin('facebook')}
                  className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
                >
                  <Facebook className="h-5 w-5 mr-3 text-blue-600" />
                  <span className="text-gray-700 font-medium">Continue with Facebook</span>
                </button>

                <button
                  onClick={() => handleSocialLogin('instagram')}
                  className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
                >
                  <Instagram className="h-5 w-5 mr-3 text-pink-600" />
                  <span className="text-gray-700 font-medium">Continue with Instagram</span>
                </button>

                <button
                  onClick={() => handleSocialLogin('apple')}
                  className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
                >
                  <Apple className="h-5 w-5 mr-3 text-gray-800" />
                  <span className="text-gray-700 font-medium">Continue with Apple</span>
                </button>
              </div>

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">or</span>
                </div>
              </div>

              {/* Email/Phone Login Options */}
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => handleMethodSelect('email')}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                >
                  <Mail className="h-6 w-6 text-blue-600 mb-2" />
                  <span className="text-sm font-medium text-gray-700">Email</span>
                </button>

                <button
                  onClick={() => handleMethodSelect('phone')}
                  className="flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                >
                  <Phone className="h-6 w-6 text-blue-600 mb-2" />
                  <span className="text-sm font-medium text-gray-700">Phone</span>
                </button>
              </div>
            </div>
          )}

          {/* Email/Phone Credentials Form */}
          {authStep === 'credentials' && (
            <form onSubmit={handlePasswordLogin} className="space-y-6">
              {loginMethod === 'email' ? (
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="appearance-none relative block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      id="phone"
                      name="phone"
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={handleChange}
                      className="appearance-none relative block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter your phone number"
                    />
                  </div>
                </div>
              )}

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className="appearance-none relative block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 mr-3 bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
                
                <button
                  type="button"
                  onClick={handleSendOTP}
                  disabled={loading}
                  className="flex-1 ml-3 bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Sending...' : 'Send OTP'}
                </button>
              </div>
            </form>
          )}

          {/* OTP Verification */}
          {authStep === 'otp' && (
            <form onSubmit={handleOTPVerification} className="space-y-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Verify OTP</h3>
                <p className="text-gray-600">
                  We've sent a verification code to{' '}
                  <span className="font-medium">
                    {loginMethod === 'email' ? formData.email : formData.phone}
                  </span>
                </p>
              </div>

              <div>
                <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter verification code
                </label>
                <input
                  id="otp"
                  name="otp"
                  type="text"
                  required
                  maxLength={6}
                  value={formData.otp}
                  onChange={handleChange}
                  className="appearance-none relative block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="000000"
                />
                <p className="mt-2 text-sm text-gray-500 text-center">
                  Demo OTP: 123456
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={handleSendOTP}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Resend code
                </button>
              </div>
            </form>
          )}

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link href="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;