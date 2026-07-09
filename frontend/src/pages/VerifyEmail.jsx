// =====================================================================
// FILE: frontend/src/pages/VerifyEmail.jsx
// DESCRIPTION: Email verification verification view.
// =====================================================================

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { CheckCircle, AlertCircle, Key, ArrowLeft } from 'lucide-react';
import { BACKEND_URL } from '../services/api';

export const VerifyEmail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [token, setToken] = useState(location.state?.token || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleVerify = async (e) => {
    if (e) e.preventDefault();
    if (!token) {
      setError('Please provide a verification token.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to verify email.');
      }

      setSuccess('Your email address has been successfully verified!');
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-run verification if token is passed during signup redirection
  useEffect(() => {
    if (location.state?.token) {
      handleVerify();
    }
  }, [location.state?.token]);

  return (
    <div className="w-screen h-screen flex justify-center items-center bg-bg-light dark:bg-bg-dark overflow-hidden relative font-sans text-slate-800 dark:text-slate-100 transition-colors duration-300">
      
      {/* Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full bg-lime-500/10 dark:bg-emerald-950/15 blur-[120px]" />
      </div>

      <div className="w-full max-w-md p-8 bg-white/40 dark:bg-bg-panelDark/30 backdrop-blur-2xl border border-emerald-500/10 dark:border-white/5 rounded-3xl shadow-2xl relative z-10 mx-4 transition-all">
        
        <div className="text-center mb-6">
          <span className="text-3xl select-none">✉️</span>
          <h1 className="text-2xl font-bold mt-2 tracking-tight">Verify Email</h1>
          <p className="text-xs text-slate-400 mt-1 select-none">Enter the token sent to your email to access protected AI features</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 px-4 py-3 bg-red-500/15 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl text-xs mb-5 animate-pulse">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success ? (
          <div className="text-center py-4 flex flex-col items-center gap-3">
            <CheckCircle className="w-12 h-12 text-emerald-500 animate-bounce" />
            <h2 className="font-semibold text-sm">Email Verified Successfully!</h2>
            <p className="text-xs text-slate-400 leading-relaxed max-w-[280px]">
              {success} Redirecting to login...
            </p>
          </div>
        ) : (
          <form onSubmit={handleVerify} className="flex flex-col gap-4">
            {/* Token */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-500 dark:text-slate-400">Verification Token</label>
              <div className="relative flex items-center">
                <Key className="w-4.5 h-4.5 absolute left-3.5 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  placeholder="verify-token:xxxxxxxxxxxx"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full pl-10.5 pr-4 py-2.5 bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/5 rounded-xl text-xs outline-none focus:ring-1 focus:ring-emerald-500/50"
                  disabled={loading}
                  required
                />
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
                'Verify Address'
              )}
            </button>
          </form>
        )}

        <div className="mt-8 text-center border-t border-slate-200 dark:border-white/5 pt-5">
          <Link to="/login" className="inline-flex items-center gap-1.5 text-xs text-slate-450 dark:text-slate-400 hover:underline">
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Login
          </Link>
        </div>

      </div>
    </div>
  );
};

export default VerifyEmail;
