import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  Wrench, AlertOctagon, CheckCircle2, AlertTriangle, 
  Layers, Settings, RefreshCw, X, ShieldAlert 
} from 'lucide-react';

export default function EquipmentInspector({ selectedCode, onClose, onStatusChanged }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [updating, setUpdating] = useState(false);

  const loadBOM = async () => {
    if (!selectedCode) return;
    setLoading(true);
    try {
      const res = await api.getEquipmentBOM(selectedCode);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBOM();
  }, [selectedCode]);

  const handleToggleStatus = async (nuevoEstado) => {
    setUpdating(true);
    try {
      await api.toggleEquipmentStatus(selectedCode, nuevoEstado);
      await loadBOM();
      if (onStatusChanged) onStatusChanged();
    } catch (err) {
      alert('Error cambiando estado del equipo');
    } finally {
      setUpdating(false);
    }
  };

  if (!selectedCode) return null;

  const eq = data?.equipo;
  const bom = data?.bom || [];

  return (
    <div className="bg-slate-900 border border-blue-500/40 rounded-2xl p-5 shadow-2xl space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xl font-black text-blue-400">{selectedCode}</span>
            <span
              className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                eq?.estado === 'OPERATIVO'
                  ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                  : eq?.estado === 'MANTENIMIENTO'
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                  : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
              }`}
            >
              {eq?.estado}
            </span>
          </div>
          <div className="text-sm font-semibold text-slate-200 mt-0.5">{eq?.nombre}</div>
          <div className="text-xs text-slate-400">
            {eq?.tipo} &bull; {eq?.modelo} ({eq?.fabricante})
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-8 text-slate-400 text-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-blue-400 mr-2" />
          Cargando despiece y telemetría del equipo...
        </div>
      ) : (
        <>
          {/* Interactive State Injection Controls */}
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2">
            <div className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">
              Control de Choque en el Gemelo Digital:
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                disabled={updating || eq?.estado === 'OPERATIVO'}
                onClick={() => handleToggleStatus('OPERATIVO')}
                className="px-3 py-1.5 rounded-lg bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-40"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Restablecer a Operativo
              </button>
              <button
                disabled={updating || eq?.estado === 'MANTENIMIENTO'}
                onClick={() => handleToggleStatus('MANTENIMIENTO')}
                className="px-3 py-1.5 rounded-lg bg-amber-600/20 text-amber-300 hover:bg-amber-600/30 border border-amber-500/30 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-40"
              >
                <Wrench className="w-3.5 h-3.5" /> Enviar a Mantenimiento
              </button>
              <button
                disabled={updating || eq?.estado === 'FALLADO'}
                onClick={() => handleToggleStatus('FALLADO')}
                className="px-3 py-1.5 rounded-lg bg-rose-600/20 text-rose-300 hover:bg-rose-600/30 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-40"
              >
                <AlertOctagon className="w-3.5 h-3.5" /> Provocar Falla / Rotura
              </button>
            </div>
          </div>

          {/* Telemetry KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
            <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[11px]">Horómetro:</span>
              <span className="font-bold text-slate-100">{eq?.horas_operacion?.toLocaleString()} h</span>
            </div>
            <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[11px]">MTBF Confiabilidad:</span>
              <span className="font-bold text-slate-100">{eq?.mtbf_horas} h</span>
            </div>
            <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[11px]">MTTR Reparación:</span>
              <span className="font-bold text-slate-100">{eq?.mttr_horas} h</span>
            </div>
            <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[11px]">Ubicación Cota Z:</span>
              <span className="font-bold text-blue-400">{eq?.posicion?.z} m</span>
            </div>
          </div>

          {/* BOM (Bill of Materials) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-blue-400" />
                Despiece Estructural — Bill of Materials (BOM)
              </h4>
              <span className="text-[11px] text-slate-400">{bom.length} componentes críticos requeridos</span>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {bom.map((b) => (
                <div
                  key={b.id}
                  className={`p-3 rounded-xl border transition ${
                    b.en_quiebre
                      ? 'bg-rose-950/20 border-rose-500/40 text-rose-200'
                      : 'bg-slate-800/40 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase text-slate-400">{b.subsistema}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        b.en_quiebre ? 'bg-rose-500/30 text-rose-300' : 'bg-slate-700 text-slate-300'
                      }`}
                    >
                      {b.criticidad}
                    </span>
                  </div>

                  <div className="font-semibold text-sm text-slate-100 mt-1">
                    {b.repuesto_nombre} <span className="font-mono text-xs text-slate-400">({b.repuesto_codigo})</span>
                  </div>

                  <div className="flex items-center justify-between text-xs mt-2 pt-2 border-t border-slate-800/60">
                    <div className="flex items-center gap-3">
                      <span>
                        Stock Mina:{' '}
                        <strong className={b.en_quiebre ? 'text-rose-400' : 'text-emerald-400'}>
                          {b.stock_actual}
                        </strong>{' '}
                        (Seg: {b.stock_seguridad})
                      </span>
                      <span>Lead Time: {b.lead_time_dias} d</span>
                    </div>

                    <span className="font-mono text-slate-300">
                      ${b.costo_usd?.toLocaleString()} USD
                    </span>
                  </div>

                  {b.en_quiebre && (
                    <div className="mt-2 p-1.5 rounded bg-rose-900/30 text-rose-300 text-[11px] flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <strong>Quiebre de stock activo:</strong> Si este componente falla, el equipo quedará paralizado sin reemplazo disponible.
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
