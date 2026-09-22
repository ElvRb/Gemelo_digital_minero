import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  ShieldCheck, AlertTriangle, Play, RefreshCw, 
  Award, TrendingUp, CheckCircle, BarChart3, HelpCircle 
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, Cell 
} from 'recharts';

export default function ResilienceLabView() {
  const [selectedScenario, setSelectedScenario] = useState('FALLA_PROVEEDOR_UNICO');
  const [horizon, setHorizon] = useState(365);
  const [loading, setLoading] = useState(false);
  const [benchmarkData, setBenchmarkData] = useState(null);

  const scenarios = [
    {
      id: 'BASE',
      code: 'E0',
      title: 'Línea Base Sin Disrupción',
      desc: 'Operación nominal normal, lead times estándar (115 d), confiabilidad regular de proveedores.',
      duration: '0 días',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    },
    {
      id: 'FALLA_PROVEEDOR_UNICO',
      code: 'E1',
      title: 'Quiebre de Proveedor Único',
      desc: 'El fabricante original de repuestos de alta criticidad queda inoperativo (disponibilidad 5%).',
      duration: '45 - 120 días',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20'
    },
    {
      id: 'CIERRE_FRONTERA',
      code: 'E2',
      title: 'Bloqueo de Vía / Corredor Logístico',
      desc: 'Bloqueo en la carretera de acceso a la mina o cierre fronterizo que triplica el Lead Time.',
      duration: '20 - 90 días',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    },
    {
      id: 'DEMANDA_EXTREMA',
      code: 'E3',
      title: 'Demanda Simultánea en Múltiples Frentes',
      desc: 'Fallas concurrentes en jumbos y bombas que duplican la tasa de consumo de piezas clave.',
      duration: 'Picos con réplica 30d',
      badgeColor: 'text-purple-400 bg-purple-500/10 border-purple-500/20'
    }
  ];

  const runBenchmark = async () => {
    setLoading(true);
    try {
      const res = await api.runBenchmark(selectedScenario, Number(horizon));
      setBenchmarkData(res);
    } catch (err) {
      console.error(err);
      alert('Error evaluando políticas de resiliencia');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runBenchmark();
  }, [selectedScenario]);

  const bestStrategy = benchmarkData?.summary?.reduce((best, curr) => {
    if (!best || curr.Downtime_Total_Horas < best.Downtime_Total_Horas) return curr;
    return best;
  }, null);

  const colors = ['#64748b', '#3b82f6', '#10b981', '#8b5cf6', '#f59e0b'];

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-emerald-950/30 to-slate-900 border border-emerald-900/40 rounded-2xl p-6 shadow-xl">
        <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
          Evaluación What-If de Disrupciones (Sección 2.6 y 3.3 del Paper)
        </span>
        <h2 className="text-2xl font-black text-white mt-2 tracking-tight">
          LABORATORIO DE RESILIENCIA Y BENCHMARK DE POLÍTICAS
        </h2>
        <p className="text-slate-300 text-sm max-w-3xl mt-1">
          Somete la cadena de suministro a pruebas de estrés bajo los escenarios del estudio (E0, E1, E2, E3)
          y evalúa el desempeño comparado de las estrategias de mitigación: Robustez (&rho;), Rapidez (&psi;) y Redundancia (&delta;).
        </p>
      </div>

      {/* Scenario Chooser Cards */}
      <div>
        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
          1. Selecciona el Escenario de Disrupción:
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => setSelectedScenario(sc.id)}
                className={`text-left p-4 rounded-xl border transition-all relative ${
                  isSelected
                    ? 'bg-slate-800/90 border-blue-500 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/50'
                    : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-black px-2 py-0.5 rounded-md border ${sc.badgeColor}`}>
                    {sc.code}
                  </span>
                  <span className="text-[11px] text-slate-400">{sc.duration}</span>
                </div>
                <div className="font-bold text-sm text-slate-100 mb-1">{sc.title}</div>
                <div className="text-xs text-slate-400 leading-relaxed line-clamp-2">{sc.desc}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Benchmark Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Table & Recommendation */}
        <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              Matriz de Resiliencia Comparada (Estrategias P0 a P4)
            </h3>
            <button
              onClick={runBenchmark}
              disabled={loading}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-blue-600/20 text-blue-300 hover:bg-blue-600/30 border border-blue-500/30 flex items-center gap-1.5 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Re-calcular
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-800/80 text-slate-400 text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="p-2.5">Estrategia</th>
                  <th className="p-2.5 text-right">Downtime (h)</th>
                  <th className="p-2.5 text-right">Reducción %</th>
                  <th className="p-2.5 text-right">Robustez (&rho;)</th>
                  <th className="p-2.5 text-right">Rapidez (&psi;)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {benchmarkData?.summary?.map((row, idx) => {
                  const isBest = bestStrategy?.Estrategia === row.Estrategia;
                  return (
                    <tr
                      key={row.Estrategia}
                      className={`hover:bg-slate-800/40 transition ${
                        isBest ? 'bg-emerald-950/20 font-medium' : ''
                      }`}
                    >
                      <td className="p-2.5 font-semibold text-slate-200 flex items-center gap-2">
                        {isBest && <Award className="w-4 h-4 text-emerald-400 shrink-0" />}
                        {row.Estrategia}
                      </td>
                      <td className="p-2.5 text-right font-mono text-slate-100">
                        {row.Downtime_Total_Horas.toLocaleString()} h
                      </td>
                      <td className="p-2.5 text-right">
                        <span
                          className={`font-bold ${
                            row.Reduccion_Downtime_Pct >= 30
                              ? 'text-emerald-400'
                              : row.Reduccion_Downtime_Pct > 0
                              ? 'text-blue-400'
                              : 'text-slate-400'
                          }`}
                        >
                          {row.Reduccion_Downtime_Pct > 0 ? `-${row.Reduccion_Downtime_Pct}%` : '0.0%'}
                        </span>
                      </td>
                      <td className="p-2.5 text-right font-mono text-slate-300">{row.robustez_rho}</td>
                      <td className="p-2.5 text-right font-mono text-slate-300">{row.rapidez_psi_dias} d</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Scientific Verdict Banner */}
          {bestStrategy && (
            <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/40 to-slate-900 border border-emerald-500/30 text-xs">
              <div className="flex items-center gap-2 font-bold text-emerald-400 text-sm mb-1">
                <CheckCircle className="w-4 h-4" />
                Estrategia Óptima Identificada: {bestStrategy.Estrategia}
              </div>
              <div className="text-slate-300 leading-relaxed">
                Logra una reducción de downtime de <strong>{bestStrategy.Reduccion_Downtime_Pct}%</strong>{' '}
                {bestStrategy.Reduccion_Downtime_Pct >= 30.0 ? (
                  <span className="text-emerald-300">
                    (&ge; 30%, superando el umbral formal establecido en la Hipótesis H1 con alta significancia).
                  </span>
                ) : (
                  <span className="text-amber-300">
                    (No supera el umbral del 30% en este escenario extremo sin combinar políticas).
                  </span>
                )}
                {' '}Reduce el impacto financiero de la parada a <strong>${(bestStrategy.Perdida_Produccion_USD / 1000).toFixed(0)}k USD</strong>.
              </div>
            </div>
          )}
        </div>

        {/* Recharts Bar Chart */}
        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <h4 className="font-bold text-slate-200 text-sm mb-1">
              Comparativa de Downtime Total (Horas/Año)
            </h4>
            <p className="text-xs text-slate-400 mb-4">Menor es mejor. Basado en corridas numéricas de 365 días.</p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={benchmarkData?.summary || []} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis 
                  dataKey="Estrategia" 
                  type="category" 
                  stroke="#94a3b8" 
                  tick={{ fontSize: 10 }} 
                  width={140} 
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val) => [`${val.toLocaleString()} horas`, 'Downtime Total']}
                />
                <Bar dataKey="Downtime_Total_Horas" radius={[0, 6, 6, 0]}>
                  {benchmarkData?.summary?.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.Reduccion_Downtime_Pct >= 30 ? '#10b981' : entry.Reduccion_Downtime_Pct > 0 ? '#3b82f6' : '#ef4444'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-3 border-t border-slate-800">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-rose-500 inline-block"/> Baseline</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block"/> Mitigación Parcial</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block"/> Resiliente (&ge;30%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
