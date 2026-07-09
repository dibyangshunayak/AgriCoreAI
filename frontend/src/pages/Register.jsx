// =====================================================================
// FILE: frontend/src/pages/Register.jsx
// DESCRIPTION: Enterprise registration page view.
// =====================================================================

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { BACKEND_URL } from '../services/api';
import Logo from '../components/Logo';

export const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (!agreeTerms) {
      setError('You must agree to the Terms and Privacy Policy.');
      return;
    }

    setLoading(true);
    try {
      const data = await register(name, email, password);
      
      // Verification token simulation details shown on signup
      setSuccess(`Account registered successfully! Verification Token: ${data.verification_token}. Redirecting...`);
      setTimeout(() => {
        // Automatically transition to the verify-email page
        navigate('/verify-email', { state: { token: data.verification_token } });
      }, 3500);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
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
            text: "signup_with",
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
      
      {/* Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-lime-500/10 dark:bg-emerald-950/15 blur-[120px]" />
      </div>

      {/* Register Card */}
      <div className="w-full max-w-md p-6 bg-white/40 dark:bg-bg-panelDark/30 backdrop-blur-2xl border border-emerald-500/10 dark:border-white/5 rounded-3xl shadow-2xl relative z-10 mx-4 transition-all overflow-y-auto max-h-[92vh]">
        
        <div className="text-center mb-5">
          <span className="text-3xl select-none block mb-1">🌾</span>
          <h1 className="text-2xl font-bold mt-1 tracking-tight">Create Account</h1>
          <p className="text-xs text-slate-400 mt-1 select-none">Start managing crops, locations, and memory diagnostics</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/15 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl text-xs mb-4.5 animate-pulse">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 px-4 py-3 bg-emerald-500/15 border border-emerald-500/20 text-emerald-600 dark:text-emerald-450 rounded-xl text-xs mb-4.5 break-all">
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {/* Full Name */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">Full Name</label>
            <div className="relative flex items-center">
              <User className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-10.5 pr-4 py-2 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50"
                disabled={loading}
                required
              />
            </div>
          </div>

          {/* Email */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">Email</label>
            <div className="relative flex items-center">
              <Mail className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                type="email"
                placeholder="farmer@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10.5 pr-4 py-2 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50"
                disabled={loading}
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">Password</label>
            <div className="relative flex items-center">
              <Lock className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10.5 pr-10 py-2 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50"
                disabled={loading}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 p-1 text-slate-400 cursor-pointer"
                disabled={loading}
              >
                {showPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">Confirm Password</label>
            <div className="relative flex items-center">
              <Lock className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full pl-10.5 pr-4 py-2 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50"
                disabled={loading}
                required
              />
            </div>
          </div>

          {/* Terms checkbox */}
          <label className="flex items-center gap-2 cursor-pointer text-[11px] select-none py-1">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              className="w-4.5 h-4.5 rounded border-slate-350 accent-emerald-600 focus:ring-emerald-500/20"
              disabled={loading}
            />
            <span className="text-slate-550 dark:text-slate-400 leading-normal font-medium">I agree to Terms and Privacy Policy</span>
          </label>

          {/* Create Button */}
          <button
            type="submit"
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer flex justify-center items-center mt-1 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? (
              <span className="inline-block border-2 border-white/30 border-t-white rounded-full w-4 h-4 animate-spin" />
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative flex py-4 items-center">
          <div className="flex-grow border-t border-slate-200 dark:border-white/5"></div>
          <span className="flex-shrink mx-4 text-slate-455 text-[10px] tracking-wider uppercase font-semibold select-none">Or signup with</span>
          <div className="flex-grow border-t border-slate-200 dark:border-white/5"></div>
        </div>

        {/* Social Actions */}
        <div className="flex flex-col gap-2.5 mb-5">
          <div id="google-signin-btn" className="w-full flex justify-center min-h-[40px]">
            <button
              onClick={handleGoogleSignIn}
              className="w-full py-2.5 bg-white/80 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl font-semibold text-xs flex justify-center items-center gap-2 hover:bg-slate-100/50 dark:hover:bg-white/10 transition-all cursor-pointer disabled:opacity-50"
              disabled={loading}
            >
              <span className="text-base select-none">🟢</span>
              <span>Register with Google</span>
            </button>
          </div>
          
          <button
            onClick={handleAppleSignIn}
            className="w-full py-2.5 bg-black text-white dark:bg-white dark:text-black rounded-xl font-semibold text-xs flex justify-center items-center gap-2 hover:opacity-90 transition-all cursor-pointer disabled:opacity-50"
            disabled={loading}
          >
            <span className="text-base select-none">🍎</span>
            <span>Register with Apple</span>
          </button>

          <button
            onClick={handleFacebookSignIn}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold text-xs flex justify-center items-center gap-2 transition-all cursor-pointer disabled:opacity-50"
            disabled={loading}
          >
            <span className="text-base select-none">🔵</span>
            <span>Register with Facebook</span>
          </button>
        </div>

        <p className="text-center text-xs text-slate-400 mt-5 select-none">
          Already have an account?{' '}
          <Link to="/login" className="text-emerald-600 dark:text-emerald-450 hover:underline font-semibold">
            Login here
          </Link>
        </p>

      </div>
    </div>
  );
};

export default Register;
