// =====================================================================
// FILE: frontend/src/pages/Login.jsx
// DESCRIPTION: Enterprise login page view with multi-provider OAuth options.
// =====================================================================

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { BACKEND_URL } from '../services/api';
import Logo from '../components/Logo';

export const Login = () => {
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const [googleClientId, setGoogleClientId] = useState('');

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/auth/config`);
        if (response.ok) {
          const data = await response.json();
          setGoogleClientId(data.google_client_id);
        }
      } catch (err) {
        console.error("Failed to load Google Auth configuration:", err);
      }
    };
    fetchConfig();
  }, []);

  useEffect(() => {
    if (googleClientId && window.google) {
      try {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: (response) => {
            handleSocialSignIn('google', response.credential);
          }
        });
        
        window.google.accounts.id.renderButton(
          document.getElementById("google-signin-btn"),
          { 
            theme: "outline", 
            size: "large", 
            width: "384",
            text: "continue_with",
            shape: "rectangular"
          }
        );
      } catch (err) {
        console.error("Error initializing Google Identity Services:", err);
      }
    }
  }, [googleClientId]);

  const handleSocialSignIn = async (provider, tokenToVerify) => {
    setError('');
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenToVerify })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `${provider} authentication failed.`);
      }

      localStorage.setItem('agri_access_token', data.access_token);
      localStorage.setItem('agri_refresh_token', data.refresh_token);
      // Fast reload token into AuthContext state
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    const mockToken = `mock-google-token:${email || 'google-farmer@example.com'}:${email ? email.split('@')[0] : 'Google Farmer'}`;
    handleSocialSignIn('google', mockToken);
  };

  const handleAppleSignIn = () => {
    const mockToken = `mock-apple-token:${email || 'apple-farmer@privaterelay.appleid.com'}:Apple Farmer`;
    handleSocialSignIn('apple', mockToken);
  };

  const handleFacebookSignIn = () => {
    const mockToken = `mock-facebook-token:${email || 'facebook-farmer@example.com'}:Facebook Farmer`;
    handleSocialSignIn('facebook', mockToken);
  };

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-bg-light dark:bg-bg-dark overflow-hidden relative font-sans text-slate-800 dark:text-slate-100 transition-colors duration-300">
      
      {/* Dynamic Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-lime-500/10 dark:bg-emerald-950/15 blur-[120px]" />
      </div>

      {/* Login Container */}
      <div className="w-full max-w-md p-8 bg-white/40 dark:bg-bg-panelDark/30 backdrop-blur-2xl border border-emerald-500/10 dark:border-white/5 rounded-3xl shadow-2xl relative z-10 mx-4 transition-all duration-350 hover:shadow-emerald-600/5">
        
        <div className="text-center mb-6">
          <span className="text-3xl select-none block mb-1">🌾</span>
          <h1 className="text-2xl font-bold mt-2 tracking-tight">Welcome Back</h1>
          <p className="text-xs text-slate-400 mt-1 select-none">Sign in to continue using AgriCore AI</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/15 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl text-xs mb-5 animate-pulse">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Social Sign-In Options */}
        <div className="flex flex-col gap-2.5 mb-5">
          <div id="google-signin-btn" className="w-full flex justify-center min-h-[40px]">
            <button
              onClick={handleGoogleSignIn}
              className="w-full py-2.5 bg-white/80 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl font-semibold text-xs flex justify-center items-center gap-2 hover:bg-slate-100/50 dark:hover:bg-white/10 transition-all cursor-pointer disabled:opacity-50"
              disabled={loading}
            >
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path fill="#EA4335" d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.6 15.02 1 12 1 7.35 1 3.39 3.65 1.5 7.5l3.9 3.03C6.35 7.42 8.94 5.04 12 5.04z" />
                <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.36H12v4.51h6.46c-.29 1.48-1.14 2.73-2.4 3.58l3.76 2.92c2.2-2.03 3.67-5.01 3.67-8.65z" />
                <path fill="#FBBC05" d="M5.4 14.53c-.25-.75-.39-1.55-.39-2.38s.14-1.63.39-2.38L1.5 6.74C.54 8.65 0 10.77 0 13s.54 4.35 1.5 6.26l3.9-3.03z" />
                <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.92l-3.76-2.92c-1.1.74-2.52 1.18-4.2 1.18-3.06 0-5.65-2.38-6.6-5.49l-3.9 3.03C3.39 20.35 7.35 23 12 23z" />
              </svg>
              <span>Continue with Google</span>
            </button>
          </div>
          
          <button
            onClick={handleAppleSignIn}
            className="w-full py-2.5 bg-black text-white dark:bg-white dark:text-black rounded-xl font-semibold text-xs flex justify-center items-center gap-2 hover:opacity-90 transition-all cursor-pointer disabled:opacity-50"
            disabled={loading}
          >
            <span className="text-sm select-none">🍎</span>
            <span>Continue with Apple</span>
          </button>

          <button
            onClick={handleFacebookSignIn}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold text-xs flex justify-center items-center gap-2 transition-all cursor-pointer disabled:opacity-50"
            disabled={loading}
          >
            <span className="text-sm select-none">🔵</span>
            <span>Continue with Facebook</span>
          </button>
        </div>

        {/* Divider */}
        <div className="relative flex py-4 items-center">
          <div className="flex-grow border-t border-slate-200 dark:border-white/5"></div>
          <span className="flex-shrink mx-4 text-slate-400 text-xxs tracking-wider uppercase font-semibold select-none">OR</span>
          <div className="flex-grow border-t border-slate-200 dark:border-white/5"></div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
          {/* Email */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400" htmlFor="email">Email</label>
            <div className="relative flex items-center">
              <Mail className="w-4 h-4 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                id="email"
                type="email"
                placeholder="farmer@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50 transition-all placeholder-slate-400"
                disabled={loading}
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400" htmlFor="password">Password</label>
            <div className="relative flex items-center">
              <Lock className="w-4 h-4 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-10 py-2.5 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50 transition-all placeholder-slate-400"
                disabled={loading}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 p-1 rounded hover:bg-slate-100 dark:hover:bg-white/5 text-slate-450 dark:text-slate-400 cursor-pointer"
                disabled={loading}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember me & Forgot Password */}
          <div className="flex justify-between items-center py-1">
            <label className="flex items-center gap-2 cursor-pointer text-xs select-none">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 accent-emerald-600 focus:ring-emerald-550/20"
                disabled={loading}
              />
              <span className="text-slate-550 dark:text-slate-450 font-medium">Remember Me</span>
            </label>
            <Link to="/forgot-password" className="text-xs text-emerald-600 dark:text-emerald-450 hover:underline font-semibold">Forgot Password?</Link>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer flex justify-center items-center mt-1.5 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? (
              <span className="inline-block border-2 border-white/30 border-t-white rounded-full w-4 h-4 animate-spin" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 mt-6 select-none">
          Don't have an account?{' '}
          <Link to="/register" className="text-emerald-600 dark:text-emerald-450 hover:underline font-semibold">
            Create Account
          </Link>
        </p>

      </div>
    </div>
  );
};

export default Login;
