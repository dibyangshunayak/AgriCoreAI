import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import { useUser } from '../context/UserContext';
import { 
  CloudRain, ShieldAlert, Check, Activity, Cpu, 
  DollarSign, Terminal, RefreshCw, Sparkles, MapPin, 
  Droplets, Wind, Calendar
} from 'lucide-react';

export const Dashboard = () => {
  const { profile } = useUser();
  const [metrics, setMetrics] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  // Simulated Tasks state for micro-interactions
  const [tasks, setTasks] = useState([
    { id: 1, text: "GPS Geotagging & coordinates validation", done: true },
    { id: 2, text: "Spray Copper Fungicide on Tomato rows (High Blight Risk)", done: false },
    { id: 3, text: "Suspend active sprinkler irrigation systems (Rain Warning)", done: false },
    { id: 4, text: "Inspect drainage canals in maize field", done: false }
  ]);

  const toggleTask = (id) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, done: !t.done } : t));
  };

  const fetchTelemetry = async () => {
    setLoadingMetrics(true);
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/metrics`, {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setMetrics(data.metrics || []);
        setAlerts(data.alerts || []);
      }
    } catch (err) {
      console.error("Failed to fetch telemetry metrics:", err);
    } finally {
      setLoadingMetrics(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  // Telemetry Aggregations
  const totalCalls = metrics.length;
  const avgLatency = totalCalls > 0 
    ? (metrics.reduce((sum, item) => sum + (item.latency || 0), 0) / totalCalls).toFixed(2) 
    : '0.00';
  const totalCost = totalCalls > 0 
    ? metrics.reduce((sum, item) => sum + (item.cost || 0), 0).toFixed(5)
    : '0.00000';
  const totalTokens = totalCalls > 0
    ? metrics.reduce((sum, item) => sum + (item.tokens || 0), 0)
    : 0;

  // Compile tools & agent occurrences
  const toolCounts = {};
  metrics.forEach(m => {
    (m.tools || []).forEach(t => {
      toolCounts[t] = (toolCounts[t] || 0) + 1;
    });
  });

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto flex flex-col gap-6 select-none">
        
        {/* Title / Description */}
        <div className="flex flex-col gap-1">
          <h2 className="text-xl font-bold text-white">Dashboard Overview</h2>
          <p className="text-xs text-slate-400">Telemetry logs, alerts, and farm metrics sync</p>
        </div>

        {/* Rain Alert Banner */}
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-center gap-3 text-amber-200">
          <ShieldAlert className="w-5 h-5 text-amber-500 shrink-0" />
          <div className="flex-1 text-xs font-semibold leading-relaxed">
            <span className="font-extrabold uppercase tracking-wider text-[10px] bg-amber-500/20 px-2 py-0.5 rounded mr-2">Rain Alert</span>
            Heavy precipitation (~35mm) forecast for this evening. Suspend active sprinkler systems and fertilizer sprays to avoid soil saturation and wash-off.
          </div>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Farm Health, Soil moisture & Weather */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            
            {/* Health Score Card */}
            <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-6 rounded-3xl flex flex-col items-center justify-between min-h-[180px]">
              <div className="flex justify-between items-center w-full text-slate-400">
                <span className="text-[11px] font-bold uppercase tracking-wider">Farm Health Index</span>
                <Sparkles className="w-4 h-4 text-emerald-500" />
              </div>
              <div className="relative my-1">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle cx="48" cy="48" r="38" stroke="currentColor" strokeWidth="6" className="text-white/5 fill-transparent" />
                  <circle cx="48" cy="48" r="38" stroke="#10b981" strokeWidth="6" strokeDasharray="238" strokeDashoffset={238 - (238 * 94) / 100} strokeLinecap="round" className="fill-transparent" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span className="text-xl font-extrabold text-white">94%</span>
                  <span className="text-[8px] uppercase tracking-wider font-extrabold text-emerald-500">Optimal</span>
                </div>
              </div>
              <p className="text-[10px] text-slate-500">Calculated from soil, GPS, and weather indices</p>
            </div>

            {/* Platform Metrics (Telemetry numbers) */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-4 rounded-2xl">
                <span className="text-[9px] font-bold uppercase text-slate-500">Avg Latency</span>
                <p className="text-xl font-extrabold text-white mt-1">{avgLatency}s</p>
              </div>
              <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-4 rounded-2xl">
                <span className="text-[9px] font-bold uppercase text-slate-500">Tokens</span>
                <p className="text-xl font-extrabold text-white mt-1">{totalTokens.toLocaleString()}</p>
              </div>
              <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-4 rounded-2xl">
                <span className="text-[9px] font-bold uppercase text-slate-500">Sourcing Cost</span>
                <p className="text-xl font-extrabold text-white mt-1">${totalCost}</p>
              </div>
              <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 p-4 rounded-2xl">
                <span className="text-[9px] font-bold uppercase text-slate-500">Agent Runs</span>
                <p className="text-xl font-extrabold text-white mt-1">{totalCalls}</p>
              </div>
            </div>

            {/* Execution Telemetry Traces Table */}
            <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 rounded-3xl p-6 flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-xs uppercase text-slate-400">Execution Telemetry Traces</h3>
                <button 
                  onClick={fetchTelemetry}
                  className="p-1.5 hover:bg-white/5 rounded-lg text-slate-450 hover:text-white transition-colors cursor-pointer"
                  title="Reload Metrics"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingMetrics ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-slate-500">
                      <th className="py-2">Latency</th>
                      <th className="py-2">Invoked Agents</th>
                      <th className="py-2">Cost</th>
                      <th className="py-2">Tools</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-slate-500 font-medium">No telemetry logged yet. Traces populate as you query the AI Chat.</td>
                      </tr>
                    ) : (
                      [...metrics].reverse().slice(0, 5).map((run, idx) => (
                        <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                          <td className="py-2.5 font-bold text-emerald-400">{run.latency ? `${run.latency.toFixed(2)}s` : '0s'}</td>
                          <td className="py-2.5 flex flex-wrap gap-1">
                            {(run.agents || []).map((agent, aIdx) => (
                              <span key={aIdx} className="px-1.5 py-0.5 bg-emerald-500/10 border border-emerald-500/10 text-emerald-400 rounded text-[9px] font-bold">
                                {agent}
                              </span>
                            ))}
                            {(run.agents || []).length === 0 && <span className="text-slate-500 italic text-[10px]">general_agent</span>}
                          </td>
                          <td className="py-2.5 text-slate-400">${(run.cost || 0).toFixed(5)}</td>
                          <td className="py-2.5 text-slate-400 text-[10px] font-mono">
                            {(run.tools || []).slice(0, 3).join(', ')}{(run.tools || []).length > 3 ? '...' : ''}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* Right Column: Tasks Checklist & Tools invocation log */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            
            {/* Checklist Card */}
            <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 rounded-3xl p-6 flex flex-col gap-4">
              <h3 className="font-bold text-xs uppercase text-slate-400 flex items-center gap-1.5 border-b border-white/5 pb-2.5">
                <Check className="w-4 h-4 text-emerald-500" />
                <span>Today's Farm Tasks</span>
              </h3>
              
              <div className="flex flex-col gap-2.5">
                {tasks.map(task => (
                  <div 
                    key={task.id} 
                    onClick={() => toggleTask(task.id)}
                    className="flex items-start gap-3 p-2.5 hover:bg-emerald-500/5 rounded-xl cursor-pointer transition-colors group"
                  >
                    <div className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                      task.done 
                        ? 'bg-emerald-600 border-emerald-600 text-white' 
                        : 'border-slate-700'
                    }`}>
                      {task.done && <Check className="w-3 h-3 stroke-[3px]" />}
                    </div>
                    <span className={`text-[11.5px] font-semibold leading-normal transition-colors ${
                      task.done ? 'text-slate-550 line-through' : 'text-slate-300'
                    }`}>
                      {task.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Tools log log */}
            <div className="bg-[#101a12] border border-slate-200/10 dark:border-white/5 rounded-3xl p-6 flex flex-col gap-4 h-full">
              <h3 className="font-bold text-xs uppercase text-slate-400 flex items-center gap-1.5">
                <Terminal className="w-4 h-4 text-emerald-500" />
                <span>Tools Invocation Logs</span>
              </h3>
              <div className="flex-1 bg-black/40 border border-white/5 rounded-2xl p-4 font-mono text-[9px] text-emerald-400 overflow-y-auto min-h-[220px] max-h-[300px]">
                <div className="flex flex-col gap-1.5">
                  <p className="text-slate-600">[+] Tool Registry synchronized.</p>
                  {Object.keys(toolCounts).length === 0 ? (
                    <p className="text-slate-650">[+] No tools called yet.</p>
                  ) : (
                    Object.entries(toolCounts).map(([tool, count], idx) => (
                      <div key={idx} className="flex justify-between border-b border-white/5 pb-1">
                        <span className="text-emerald-400">&gt; tool:{tool}</span>
                        <span className="text-slate-500">{count}x</span>
                      </div>
                    ))
                  )}
                  <p className="text-slate-600 mt-2">[+] Observation listener active.</p>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </AppLayout>
  );
};

export default Dashboard;
