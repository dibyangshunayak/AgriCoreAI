import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Globe, Sun, CloudSun, CloudRain, Cloud, RefreshCw } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useChat } from '../hooks/useChat';
import { useLocation } from '../hooks/useLocation';

export const Header = ({ onMenuToggle }) => {
  const navigate = useNavigate();
  const { profile } = useUser();
  const { isThinking, isStreaming } = useChat();
  const { location, loading, requestLocation } = useLocation();

  const isOnline = !isThinking && !isStreaming;
  const userName = profile?.name || 'User';
  const initials = userName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U';
  const lang = profile?.preferred_language || 'en';

  const getWeatherIcon = (code) => {
    if (code === 0) return <Sun className="w-3.5 h-3.5 text-amber-400" />;
    if ([1, 2, 3].includes(code)) return <CloudSun className="w-3.5 h-3.5 text-blue-300" />;
    if ([61, 63, 65, 80, 81, 82, 95, 96, 99].includes(code)) return <CloudRain className="w-3.5 h-3.5 text-sky-450 animate-pulse" />;
    return <Cloud className="w-3.5 h-3.5 text-slate-400" />;
  };

  return (
    <header className="flex items-center justify-between px-4 md:px-6 h-[60px] border-b border-white/[0.06] bg-[#0F172A]/80 backdrop-blur-sm flex-shrink-0 select-none z-20">
      {/* Left: mobile menu + assistant name */}
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={onMenuToggle}
          className="md:hidden p-2 -ml-1 rounded-lg text-[#94A3B8] hover:text-white hover:bg-white/10 transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5">
            {/* Status dot */}
            <div className={`relative flex items-center justify-center`}>
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-[#10B981]' : 'bg-amber-400 animate-pulse'}`} />
              {isOnline && (
                <span className="absolute w-2 h-2 rounded-full bg-[#10B981] animate-ping opacity-50" />
              )}
            </div>
            <span className="text-xs text-[#94A3B8] font-medium hidden sm:block">
              {isThinking ? 'Thinking...' : isStreaming ? 'Streaming...' : 'AgriCore AI'}
            </span>
          </div>
        </div>
      </div>

      {/* Center: page title on desktop */}
      <div className="hidden md:flex items-center gap-2 absolute left-1/2 -translate-x-1/2">
        <span className="text-[13px] font-medium text-[#64748B]">Agriculture Intelligence Platform</span>
      </div>

      {/* Right: language and avatar */}
      <div className="flex items-center gap-1.5">
        {/* Location & Weather Widget */}
        <div className="flex items-center gap-2 border-r border-white/10 pr-2 mr-2">
          {location ? (
            <div className="flex flex-col items-end text-right select-none">
              <span className="text-[10px] text-slate-400 font-medium max-w-[120px] truncate">
                {location.city || location.formatted_location.split(',')[0]}
              </span>
              {location.weather && (
                <div className="flex items-center gap-1 mt-0.5">
                  {getWeatherIcon(location.weather.code)}
                  <span className="text-[11px] font-bold text-[#10B981]">{location.weather.temp}°C</span>
                </div>
              )}
            </div>
          ) : (
            <span className="text-[10px] text-slate-500 font-medium">No Location</span>
          )}

          <button
            onClick={requestLocation}
            disabled={loading}
            className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-white/10 transition-colors"
            title="Detect My Location & Weather"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>

        {/* Language indicator */}
        <button
          onClick={() => navigate('/settings')}
          className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-white/10 transition-colors text-xs font-medium"
          title="Language settings"
        >
          <Globe className="w-3.5 h-3.5" />
          <span className="uppercase font-semibold">{lang}</span>
        </button>


        {/* Avatar */}
        <button
          onClick={() => navigate('/settings')}
          className="w-8 h-8 rounded-full bg-gradient-to-br from-[#10B981] to-[#0891b2] flex items-center justify-center text-white text-xs font-bold hover:opacity-90 transition-opacity ml-1"
          title={userName}
        >
          {initials}
        </button>
      </div>
    </header>
  );
};

export default Header;


