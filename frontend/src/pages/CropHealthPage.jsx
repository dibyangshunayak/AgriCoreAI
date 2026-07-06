import React from 'react';
import AppLayout from '../components/AppLayout';
import { Sparkles, ShieldCheck, Activity, Check } from 'lucide-react';

const DEMO_FARM_HEALTH = {
  score: 87,
  soil_moisture: 72,
  nitrogen_level: 'Adequate',
  phosphorus_level: 'Low',
  potassium_level: 'Adequate',
  ph: 6.8,
  last_irrigation: '2026-07-02',
  next_irrigation_due: '2026-07-05',
};

export const CropHealthPage = () => {
  const health = DEMO_FARM_HEALTH;

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto flex flex-col gap-6 select-none">
        {/* Title */}
        <div className="flex flex-col gap-1">
          <h2 className="text-xl font-bold text-white">Crop Health & Soil Telemetry</h2>
          <p className="text-xs text-slate-400">Nutrient analytics and field growth indexing</p>
        </div>

        {/* Top Health Index Gauge & Planner recommendation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Health Index gauge */}
          <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-6 rounded-3xl flex flex-col items-center justify-between min-h-[220px]">
            <div className="flex justify-between items-center w-full text-slate-400">
              <span className="text-[11px] font-bold uppercase tracking-wider">Farm Health Index</span>
              <Sparkles className="w-4 h-4 text-emerald-500" />
            </div>
            
            <div className="relative my-2">
              <svg className="w-28 h-28 transform -rotate-90">
                <circle cx="56" cy="56" r="45" stroke="currentColor" strokeWidth="8" className="text-white/5 fill-transparent" />
                <circle cx="56" cy="56" r="45" stroke="#10b981" strokeWidth="8" strokeDasharray="282" strokeDashoffset={282 - (282 * (health.score || 94)) / 100} strokeLinecap="round" className="fill-transparent" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-2xl font-extrabold text-white">{health.score || 94}%</span>
                <span className="text-[9px] uppercase tracking-wider font-extrabold text-emerald-500">Optimal</span>
              </div>
            </div>
            
            <p className="text-[10px] text-slate-400 text-center">Growth quality scored via satellite N-Index & soil sensors</p>
          </div>

          {/* Smart Crop Planner recommendation */}
          <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-6 rounded-3xl flex flex-col justify-between min-h-[220px]">
            <div className="flex justify-between items-center text-slate-400">
              <span className="text-[11px] font-bold uppercase tracking-wider">Crop Planner Advice</span>
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
            </div>
            
            <div className="flex flex-col gap-1 my-2">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Harvest Suitability Match</p>
              <p className="text-xl font-extrabold text-emerald-400">Sweet Corn / Tomato</p>
              
              <div className="flex gap-2.5 mt-2.5 text-xxs font-semibold">
                <span className="bg-emerald-500/15 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">pH: {health.ph || 6.8} (Optimal)</span>
                <span className="bg-emerald-500/15 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">NPK: Balanced</span>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 leading-relaxed">System logs show nitrogen content matches Kharif season defaults.</p>
          </div>
        </div>

        {/* Detailed Soil Metrics Card */}
        <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-xs tracking-wide uppercase text-slate-400 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-emerald-500" />
            <span>Soil Chemical Analytics</span>
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white/5 p-4 rounded-2xl flex flex-col gap-1.5 text-center">
              <span className="text-[9px] font-extrabold text-slate-450 uppercase tracking-widest">Soil Moisture</span>
              <span className="text-lg font-bold text-white">{health.soil_moisture}%</span>
              <span className="text-[9px] text-emerald-500 font-bold">Good</span>
            </div>
            <div className="bg-white/5 p-4 rounded-2xl flex flex-col gap-1.5 text-center">
              <span className="text-[9px] font-extrabold text-slate-450 uppercase tracking-widest">Nitrogen (N)</span>
              <span className="text-lg font-bold text-white">{health.nitrogen_level}</span>
              <span className="text-[9px] text-emerald-500 font-bold">Adequate</span>
            </div>
            <div className="bg-white/5 p-4 rounded-2xl flex flex-col gap-1.5 text-center">
              <span className="text-[9px] font-extrabold text-slate-450 uppercase tracking-widest">Phosphorus (P)</span>
              <span className="text-lg font-bold text-white">{health.phosphorus_level}</span>
              <span className="text-[9px] text-amber-500 font-bold">Slightly Low</span>
            </div>
            <div className="bg-white/5 p-4 rounded-2xl flex flex-col gap-1.5 text-center">
              <span className="text-[9px] font-extrabold text-slate-450 uppercase tracking-widest">Potassium (K)</span>
              <span className="text-lg font-bold text-white">{health.potassium_level}</span>
              <span className="text-[9px] text-emerald-500 font-bold">Optimal</span>
            </div>
          </div>
        </div>

        {/* Irrigation checklist / schedule */}
        <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 rounded-3xl p-6 flex flex-col gap-4">
          <h3 className="font-bold text-xs tracking-wide uppercase text-slate-400">Field Irrigation Schedule</h3>
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center text-xs border border-white/5 p-4 rounded-2xl">
            <div>
              <p className="text-slate-400 font-medium">Last Irrigation Session</p>
              <p className="text-base font-bold text-white mt-1">{health.last_irrigation}</p>
            </div>
            <div className="h-px w-full sm:h-8 sm:w-px bg-white/10" />
            <div>
              <p className="text-slate-400 font-medium">Next Recommended Watering</p>
              <p className="text-base font-bold text-amber-400 mt-1">{health.next_irrigation_due} (Adjusted for rain alert)</p>
            </div>
            <div className="h-px w-full sm:h-8 sm:w-px bg-white/10" />
            <span className="text-[9.5px] font-extrabold text-emerald-600 dark:text-emerald-450 bg-emerald-500/15 px-3 py-1 rounded-full flex items-center gap-1 select-none">
              <Check className="w-3.5 h-3.5" /> Auto-sync complete
            </span>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default CropHealthPage;
