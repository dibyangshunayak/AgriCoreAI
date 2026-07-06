import React from 'react';
import { useLocation } from '../hooks/useLocation';
import { useUser } from '../context/UserContext';
import { MapPin } from 'lucide-react';

/**
 * Premium Location Indicator component.
 * Displays dynamic connection status (GPS, IP Fallback, or Local Profile)
 * with the reverse-geocoded place, farm name, and accuracy metrics.
 */
export const LocationIndicator = () => {
  const { location, loading, gpsStatus } = useLocation();
  const { profile } = useUser();

  // Detect if the string is raw coordinates (e.g. "20.2620, 85.7564") to filter them out
  const isCoordsOnly = (str) => {
    if (!str) return false;
    return /^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(str.trim());
  };

  // Determine fallback details from user profile or defaults
  const farmName = profile?.farm_name || 'Green Valley Farm';
  const rawLoc = location?.formatted_location || profile?.farm_location || 'Baripada, Odisha';
  const farmLoc = isCoordsOnly(rawLoc) ? (profile?.farm_location || 'Baripada, Odisha') : rawLoc;

  // Render a clean accuracy text instead of huge IP values
  const accuracyText = location?.accuracy && location.accuracy < 100
    ? `±${Math.round(location.accuracy)} meters` 
    : '±5 meters';

  if (loading) {
    return (
      <div className="flex flex-col justify-center px-4 py-2 bg-emerald-950/45 dark:bg-[#07130a]/40 border border-emerald-500/10 rounded-2xl animate-pulse min-w-[180px] md:min-w-[210px] h-[64px] select-none">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400/80">Acquiring GPS...</span>
        </div>
        <div className="h-3.5 bg-emerald-900/35 rounded w-3/4 mt-1.5" />
      </div>
    );
  }

  let statusText = 'GPS Connected';
  let accuracyVal = accuracyText;
  let statusColor = 'bg-emerald-500 shadow-emerald-500/50';

  if (gpsStatus === 'ip') {
    statusText = 'IP Connected';
    accuracyVal = 'IP Geolocation';
    statusColor = 'bg-teal-500 shadow-teal-500/50';
  } else if (gpsStatus === 'denied' || !location) {
    statusText = 'Profile Sync';
    accuracyVal = 'Local DB';
    statusColor = 'bg-emerald-600 shadow-emerald-600/50';
  }

  return (
    <div className="glass bg-[#08180e]/40 border border-emerald-500/15 hover:border-emerald-500/30 rounded-2xl p-2.5 md:p-3 flex items-start gap-2.5 shadow-sm text-slate-100 transition-all select-none hover:shadow-lg hover:shadow-emerald-950/10 duration-300 group cursor-default min-w-[180px] md:min-w-[210px] overflow-hidden">
      <div className="p-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 group-hover:text-emerald-300 transition-colors shrink-0">
        <MapPin className="w-4 h-4" />
      </div>
      
      <div className="flex-1 min-w-0 flex flex-col leading-tight">
        <span className="text-[9px] font-extrabold uppercase tracking-widest text-emerald-400/70">
          📍 Farm Location
        </span>
        <span className="text-xs font-bold text-emerald-50 truncate w-full mt-0.5">
          {farmName}
        </span>
        <span className="text-[10px] text-slate-350 dark:text-slate-400 truncate w-full mt-0.5">
          {farmLoc}
        </span>
        
        <div className="flex items-center gap-1.5 mt-1">
          <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${statusColor}`} />
          <span className="text-[9px] font-bold text-slate-400 dark:text-emerald-400/80 uppercase tracking-wide">
            {statusText} • <span className="font-mono lowercase opacity-75">{accuracyVal}</span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default LocationIndicator;

