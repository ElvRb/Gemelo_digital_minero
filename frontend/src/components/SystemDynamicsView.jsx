import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  Play, RefreshCw, Sliders, TrendingDown, 
  Activity, AlertOctagon, DollarSign, CheckCircle2 
} from 'lucide-react';
import { 
  LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

export default function SystemDynamicsView() {
  const [horizon, setHorizon] = useState(365);
  const [leadTimeMult, setLeadTimeMult] = useState(1.0);
  const [demandMult, setDemandMult] = useState(1.0);
  const [supplierAvail, setSupplierAvail] = useState(1.0);
  const [localRepair, setLocalRepair] = useState(false);
  const [local3D, setLocal3D] = useState(false);

  const [loading, setLoading] = useState(false);
  const [simResults, setSimResults] = useState(null);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const res = await api.runSystemDynamics({
        horizon_days: Number(horizon),
        lead_time_multiplier: Number(leadTimeMult),
        demand_multiplier: Number(demandMult),
        supplier_availability: Number(supplierAvail),
        local_repair_active: Boolean(localRepair),
        local_3d_active: Boolean(local3D),
        random_seed: 42
      });
      setSimResults(res);
    } catch (err) {
      console.error(err);
      alert('Error ejecutando Dinámica de Sistemas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/40 rounded-2xl p-6 shadow-xl">
        <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
          Ecuaciones Diferenciales y Retardos No Lineales
        </span>
        <h2 className="text-2xl font-black text-white mt-2 tracking-tight">
          SIMULACIÓN DE DINÁMICA DE SISTEMAS (SYSTEM DYNAMICS)
        </h2>
        <p className="text-slate-300 text-sm max-w-3xl mt-1">
          Modelo matemático continuo de stocks y flujos con retardo de reposición de tercer orden (DELAY3).
          Evalúa cómo las perturbaciones en el tiempo de entrega y la demanda se propagan hacia la disponibilidad de flota.
        </p>

        {/* Math Equations Strip */}
        <div className="mt-4 p-3 bg-slate-950/60 border border-slate-800 rounded-xl flex flex-wrap gap-4 text-xs font-mono text-slate-300">
          <div><span className="text-indigo-400 font-bold">Balance Inventario:</span> I(t) = I(0) + &int; [R(&tau;) - C(&tau;)] d&tau;</div>
          <div><span className="text-amber-400 font-bold">Retardo Pipeline:</span> R(t) = DELAY3(P(t), L(t))</div>
          <div><span className="text-emerald-400 font-bold">Disponibilidad Flota:</span> A(t) = 1 - &sum; [w_ij &middot; S_i(t)]</div>
        </div>
      </div>

      {/* Control Panel & KPIs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sliders Form */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 font-bold text-slate-100 text-base pb-2 border-b border-slate-800">
            <Sliders className="w-5 h-5 text-blue-400" />
            Parámetros del Experimento
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300">Horizonte de Simulación:</span>
              <span className="font-bold text-blue-400">{horizon} días</span>
            </div>
            <input
              type="range"
              min="90"
              max="730"
              step="30"
              value={horizon}
              onChange={(e) => setHorizon(e.target.value)}
              className="w-full accent-blue-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300">Multiplicador Lead Time:</span>
              <span className="font-bold text-amber-400">{leadTimeMult}x ({Math.round(115 * leadTimeMult)} d)</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="3.5"
              step="0.1"
              value={leadTimeMult}
              onChange={(e) => setLeadTimeMult(e.target.value)}
              className="w-full accent-amber-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300">Multiplicador Tasa de Fallas (&lambda;):</span>
              <span className="font-bold text-rose-400">{demandMult}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="3.0"
              step="0.1"
              value={demandMult}
              onChange={(e) => setDemandMult(e.target.value)}
              className="w-full accent-rose-500 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300">Disponibilidad Proveedor Crítico:</span>
              <span className="font-bold text-emerald-400">{Math.round(supplierAvail * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={supplierAvail}
              onChange={(e) => setSupplierAvail(e.target.value)}
              className="w-full accent-emerald-500 cursor-pointer"
            />
          </div>

          <div className="pt-2 border-t border-slate-800 space-y-2">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Políticas de Mitigación In-Situ:</div>
            
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={localRepair}
                onChange={(e) => setLocalRepair(e.target.checked)}
                className="rounded accent-blue-600"
              />
              <span>Taller de Recuperación Local (LT max 16 días)</span>
            </label>

            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={local3D}
                onChange={(e) => setLocal3D(e.target.checked)}
                className="rounded accent-blue-600"
              />
              <span>Celda de Impresión Aditiva 3D (LT max 4 días)</span>
            </label>
          </div>

          <button
            onClick={runSimulation}
            disabled={loading}
            className="w-full mt-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-sm transition shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
            {loading ? 'Integrando Ecuaciones...' : 'Ejecutar Dinámica de Sistemas'}
          </button>
        </div>

        {/* Results Overview */}
        <div className="lg:col-span-8 flex flex-col justify-between space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-medium">Downtime Total</div>
              <div className="text-2xl font-black text-rose-400 mt-1">
                {simResults?.kpis?.downtime_total_horas?.toLocaleString() ?? 0} <span className="text-xs font-normal text-slate-400">h</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Horas acumuladas</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-medium">Quiebres de Stock</div>
              <div className="text-2xl font-black text-amber-400 mt-1">
                {simResults?.kpis?.stockouts_totales ?? 0}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Veces stock = 0</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-medium">Pérdida Económica</div>
              <div className="text-2xl font-black text-slate-100 mt-1">
                ${((simResults?.kpis?.perdida_produccion_usd ?? 0) / 1000).toFixed(0)}k
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Impacto financiero</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 font-medium">Disponibilidad Final</div>
              <div className="text-2xl font-black text-emerald-400 mt-1">
                {simResults?.kpis?.disponibilidad_flota_pct ?? 0}%
              </div>
              <div className="text-[11px] text-slate-500 mt-1">{simResults?.kpis?.equipos_operativos_final ?? 30} / 33 equipos</div>
            </div>
          </div>

          {/* Chart 1: Inventory Stocks & Pipeline In-Transit */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex-1">
            <h4 className="text-sm font-bold text-slate-200 mb-2 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" />
              Evolución de Stocks: Inventario Físico vs. Órdenes en Tránsito
            </h4>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={simResults?.time_series || []}>
                  <defs>
                    <linearGradient id="colorInv" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="colorTransit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} 
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }} />
                  <Area type="monotone" dataKey="inventory_level" name="Inventario en Almacén" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorInv)" />
                  <Area type="monotone" dataKey="in_transit" name="Órdenes en Tránsito (DELAY3)" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" fillOpacity={1} fill="url(#colorTransit)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Chart 2: Fleet Reliability & Downtime Curves */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
        <h4 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
          <TrendingDown className="w-4 h-4 text-emerald-400" />
          Confiabilidad Operativa de Mina: Equipos Operativos vs. Equipos Detenidos por Falta de Repuesto
        </h4>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={simResults?.time_series || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 35]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }} />
              <Line type="monotone" dataKey="operative_equipment" name="Equipos Operativos en Frente" stroke="#10b981" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="stopped_equipment" name="Equipos Detenidos por Stockout" stroke="#ef4444" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
