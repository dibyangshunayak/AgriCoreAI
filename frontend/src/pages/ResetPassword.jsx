// =====================================================================
// FILE: frontend/src/pages/ResetPassword.jsx
// DESCRIPTION: Reset password page view.
// =====================================================================


import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Eye, EyeOff, Key, AlertCircle } from 'lucide-react';
import { BACKEND_URL } from '../services/api';

export const ResetPassword = () => {
  const navigate = useNavigate();
  
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!token || !password) {
      setError('Token and password are required.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to reset password.');
      }

      setSuccess('Password updated successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-bg-light dark:bg-bg-dark overflow-hidden relative font-sans text-slate-800 dark:text-slate-100">
      {/* Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-emerald-400/10 dark:bg-emerald-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-lime-400/10 dark:bg-emerald-950/15 blur-[120px]" />
      </div>

      <div className="w-full max-w-md p-8 bg-white/40 dark:bg-bg-panelDark/30 backdrop-blur-2xl border border-emerald-500/10 dark:border-white/5 rounded-3xl shadow-2xl relative z-10 mx-4 transition-all">
        <div className="text-center mb-8">
          <span className="text-3xl">🛡</span>
          <h1 className="text-2xl font-bold mt-2 tracking-tight">Reset Password</h1>
          <p className="text-xs text-slate-400 mt-1.5 select-none">Enter your recovery token to configure a new password</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/15 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl text-xs mb-6 animate-pulse">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 px-4 py-3 bg-emerald-500/15 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs mb-6">
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Recovery Token */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400" htmlFor="token">Recovery Token</label>
            <div className="relative flex items-center">
              <Key className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                id="token"
                type="text"
                placeholder="reset-token:farmer@example.com"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full pl-10.5 pr-4 py-3 bg-white/50 dark:bg-white/5 border border-emerald-500/10 dark:border-white/5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-emerald-500/20 dark:focus:ring-emerald-400/20 transition-all placeholder-slate-400 dark:placeholder-slate-500"
                disabled={loading}
                required
              />
            </div>
          </div>

          {/* New Password */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400" htmlFor="password">New Password</label>
            <div className="relative flex items-center">
              <Lock className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10.5 pr-10.5 py-3 bg-white/50 dark:bg-white/5 border border-emerald-500/10 dark:border-white/5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-emerald-500/20 dark:focus:ring-emerald-400/20 transition-all placeholder-slate-400 dark:placeholder-slate-500"
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

          <button
            type="submit"
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold text-sm shadow-md hover:shadow-lg transition-all cursor-pointer flex justify-center items-center mt-2 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? (
              <span className="inline-block border-2 border-white/30 border-t-white rounded-full w-4 h-4 animate-spin" />
            ) : (
              'Reset Password'
            )}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 mt-6 select-none">
          Remember your details?{' '}
          <Link to="/login" className="text-emerald-600 dark:text-emerald-400 hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default ResetPassword;
