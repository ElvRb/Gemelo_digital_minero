import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  Cpu, Users, Play, RefreshCw, CheckCircle2, 
  GitBranch, ShieldCheck, Scale, ArrowRight, Activity 
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

export default function MultiAgentView() {
  const [strategy, setStrategy] = useState('ESTRATEGIA_C');
  const [scenario, setScenario] = useState('BASE');
  const [horizon, setHorizon] = useState(365);
  const [loadingABM, setLoadingABM] = useState(false);
  const [abmResult, setAbmResult] = useState(null);

  const [loadingHyp, setLoadingHyp] = useState(false);
  const [hypResult, setHypResult] = useState(null);

  const runABMSim = async () => {
    setLoadingABM(true);
    try {
      const res = await api.runABM({
        horizon_days: Number(horizon),
        strategy_code: strategy,
        scenario_type: scenario,
        random_seed: 42
      });
      setAbmResult(res);
    } catch (err) {
      console.error(err);
      alert('Error ejecutando simulación multi-agente SimPy');
    } finally {
      setLoadingABM(false);
    }
  };

  const evaluateHypothesis = async () => {
    setLoadingHyp(true);
    try {
      const res = await api.getHypothesis(scenario, strategy);
      setHypResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHyp(false);
    }
  };

  useEffect(() => {
    runABMSim();
    evaluateHypothesis();
  }, [strategy, scenario]);

  const agentClasses = [
    { name: 'EquipmentAgent', desc: 'Monitorea desgaste de 33 activos, genera fallas estocásticas y demanda repuestos.', icon: '🚜' },
    { name: 'WarehouseAgent', desc: 'Gestiona inventario con política (s, S), revisa ROP y despacha por criticidad.', icon: '📦' },
    { name: 'SupplierAgent', desc: 'Procesa órdenes internacionales, modela colapsos de fábrica y atrasos aduaneros.', icon: '🏭' },
    { name: 'TransportAgent', desc: 'Simula tránsito en corredor logístico y gestiona rutas alternas ante bloqueos.', icon: '🚚' },
    { name: 'MaintenanceAgent', desc: 'Dispone de cuadrillas especializadas para reemplazo y pruebas operativas.', icon: '🔧' }
  ];

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-purple-950/30 to-slate-900 border border-purple-900/40 rounded-2xl p-6 shadow-xl">
        <span className="text-xs font-bold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-full border border-purple-500/20">
          Simulación Basada en Agentes (ABM) con SimPy
        </span>
        <h2 className="text-2xl font-black text-white mt-2 tracking-tight">
          INTERACCIÓN DESCENTRALIZADA DE AGENTES & EVALUACIÓN FORMAL DE HIPÓTESIS
        </h2>
        <p className="text-slate-300 text-sm max-w-3xl mt-1">
          Modelado de eventos discretos donde 5 clases de agentes autónomos toman decisiones independientes
          con reglas de negociación y restricciones de capacidad. Verificación rigurosa de H0 vs H1.
        </p>
      </div>

      {/* Agents Architecture Pill Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {agentClasses.map((ag) => (
          <div key={ag.name} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5">
            <div className="text-2xl mb-1.5">{ag.icon}</div>
            <div className="font-bold text-xs text-slate-200">{ag.name}</div>
            <div className="text-[11px] text-slate-400 leading-tight mt-1">{ag.desc}</div>
          </div>
        ))}
      </div>

      {/* Interactive Controls & Live ABM Run */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2 font-bold text-slate-100 text-base">
            <Cpu className="w-5 h-5 text-purple-400" />
            Configuración de la Simulación SimPy
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-purple-500"
            >
              <option value="ESTRATEGIA_A">Estrategia A (Baseline / P0)</option>
              <option value="ESTRATEGIA_B">Estrategia B (Safety Stock +100% / P2)</option>
              <option value="ESTRATEGIA_C">Estrategia C (Dual Sourcing / P1)</option>
              <option value="ESTRATEGIA_D">Estrategia D (Reparación Local)</option>
              <option value="ESTRATEGIA_E">Estrategia E (Celda 3D Local)</option>
              <option value="ESTRATEGIA_HIBRIDA">Estrategia Híbrida (Combinada / P3)</option>
            </select>

            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-purple-500"
            >
              <option value="BASE">E0: Línea Base</option>
              <option value="FALLA_PROVEEDOR_UNICO">E1: Falla Proveedor Único</option>
              <option value="CIERRE_FRONTERA">E2: Bloqueo de Vía</option>
              <option value="DEMANDA_EXTREMA">E3: Demanda Extrema</option>
            </select>

            <button
              onClick={runABMSim}
              disabled={loadingABM}
              className="bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs py-2 px-4 rounded-lg flex items-center gap-1.5 transition disabled:opacity-50 shadow-md shadow-purple-600/20"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingABM ? 'animate-spin' : ''}`} />
              {loadingABM ? 'Simulando...' : 'Re-ejecutar SimPy'}
            </button>
          </div>
        </div>

        {/* ABM Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3.5">
            <div className="text-xs text-slate-400">Total Fallas Generadas</div>
            <div className="text-2xl font-black text-slate-100 mt-1">{abmResult?.total_failures ?? 0}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Eventos de rotura</div>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3.5">
            <div className="text-xs text-slate-400">Quiebres de Stock</div>
            <div className="text-2xl font-black text-rose-400 mt-1">{abmResult?.total_stockouts ?? 0}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Demanda no atendida</div>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3.5">
            <div className="text-xs text-slate-400">Downtime Acumulado</div>
            <div className="text-2xl font-black text-amber-400 mt-1">
              {Number(abmResult?.cumulative_downtime_hours ?? 0).toLocaleString()} <span className="text-xs font-normal">h</span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">Horas de detención flota</div>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3.5">
            <div className="text-xs text-slate-400">Pérdida Económica</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">
              ${((abmResult?.production_loss_usd ?? 0) / 1000).toFixed(0)}k <span className="text-xs font-normal">USD</span>
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">$14,500/h parada</div>
          </div>
        </div>

        {/* Chart: ABM Trace */}
        <div className="mt-4">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-400" />
            Traza Temporal de la Simulación Multi-Agente (Inventario, Tránsito y Máquinas Detenidas)
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={abmResult?.time_series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '6px' }} />
                <Line type="stepAfter" dataKey="current_stock" name="Stock en Almacén" stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line type="stepAfter" dataKey="in_transit" name="En Tránsito Proveedor" stroke="#f59e0b" strokeWidth={2} strokeDasharray="3 3" dot={false} />
                <Line type="stepAfter" dataKey="stopped_machines" name="Máquinas en Espera de Repuesto" stroke="#ef4444" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Scientific Hypothesis Formal Verdict (H0 vs H1) */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <div>
            <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
              <Scale className="w-5 h-5 text-emerald-400" />
              Evaluación Formal de la Hipótesis Científica
            </h3>
            <p className="text-xs text-slate-400">Validación formal mediante test no paramétrico de Mann-Whitney U y Bootstrap (10,000 réplicas, IC 95%)</p>
          </div>
          <span className="text-xs font-mono text-slate-400">&alpha; = 0.05 | Umbral = &ge; 30%</span>
        </div>

        {hypResult && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-center">
            <div className="md:col-span-5 p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30">
              <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">Veredicto Estadístico</div>
              <div className="text-xl font-black text-emerald-300 mt-1 mb-2">
                {hypResult.verdict}
              </div>
              <div className="space-y-1 text-xs text-slate-300">
                <div>&bull; Reducción Estimada: <strong className="text-emerald-400">{hypResult.reduccion_estimada_pct.toFixed(1)}%</strong> (Umbral &ge; 30.0%)</div>
                <div>&bull; IC Bootstrap 95%: <strong className="text-slate-200">{hypResult.ci95_str}</strong></div>
                <div>&bull; p-valor (Mann-Whitney): <strong className="text-emerald-400">{hypResult.p_value.toExponential(4)}</strong> (&lt; 0.05)</div>
              </div>
            </div>

            <div className="md:col-span-7 bg-slate-950/60 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 space-y-2">
              <div className="font-bold text-slate-200 border-b border-slate-800 pb-1">Mecanismo Causal y Conclusión:</div>
              <div className="text-[11px] text-slate-400 leading-relaxed">
                {hypResult.conclusion}
              </div>
              <div className="text-[10px] text-slate-500 pt-1">
                Baseline Downtime: {hypResult.baseline_mean_dt} h &rarr; Estrategia Resiliente: {hypResult.strategy_mean_dt} h
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
