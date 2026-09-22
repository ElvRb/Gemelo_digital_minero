import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  CheckCircle2, AlertTriangle, XCircle, Camera, RefreshCw, 
  Package, ShieldAlert, Truck, ArrowUpRight, Gauge, Clock, Eye 
} from 'lucide-react';
import Mine3DViewer from './Mine3DViewer';
import EquipmentInspector from './EquipmentInspector';

export default function DigitalTwinView() {
  const [loading, setLoading] = useState(true);
  const [twinState, setTwinState] = useState(null);
  const [fleet, setFleet] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [fleetFilter, setFleetFilter] = useState('ALL');
  const [selectedEquipmentCode, setSelectedEquipmentCode] = useState('ST-01');
  
  // Snapshot form state
  const [snapName, setSnapName] = useState(`SNAPSHOT_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`);
  const [snapNotes, setSnapNotes] = useState('Captura digital antes de ensayos de disrupción');
  const [snapSubmitting, setSnapSubmitting] = useState(false);
  const [snapSuccess, setSnapSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [stateRes, fleetRes, invRes, snapRes] = await Promise.all([
        api.getDigitalTwinState(),
        api.getDigitalTwinFleet(),
        api.getDigitalTwinInventory(),
        api.getDigitalTwinSnapshots()
      ]);
      setTwinState(stateRes);
      setFleet(fleetRes);
      setInventory(invRes);
      setSnapshots(snapRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCaptureSnapshot = async (e) => {
    e.preventDefault();
    setSnapSubmitting(true);
    try {
      const res = await api.captureSnapshot(snapName, snapNotes);
      setSnapSuccess(`Snapshot guardado exitosamente con ID #${res.id}`);
      const updatedSnaps = await api.getDigitalTwinSnapshots();
      setSnapshots(updatedSnaps);
      setTimeout(() => setSnapSuccess(''), 4000);
    } catch (err) {
      alert('Error al guardar snapshot');
    } finally {
      setSnapSubmitting(false);
    }
  };

  const filteredFleet = fleet.filter((eq) => {
    if (fleetFilter === 'ALL') return true;
    return eq.estado === fleetFilter;
  });

  if (loading && !twinState) {
    return (
      <div className="flex items-center justify-center p-20 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mr-3" />
        <span>Sincronizando estado físico del Gemelo Digital...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-blue-900/40 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="relative z-10">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20">
            Espejo Físico-Digital en Tiempo Real
          </span>
          <h2 className="text-2xl font-black text-white mt-2 tracking-tight">
            ESTADO OPERACIONAL DEL GEMELO DIGITAL (DIGITAL TWIN CORE)
          </h2>
          <p className="text-slate-300 text-sm max-w-3xl mt-1">
            Topología 3D de la mina subterránea, monitoreo de 33 equipos en frentes de trabajo, despiece de componentes (BOM)
            e inventario de repuestos críticos. Punto de partida para ensayos What-If y simulación de disrupciones.
          </p>
        </div>
        <div className="absolute right-6 top-1/2 -translate-y-1/2 opacity-10 hidden md:block pointer-events-none">
          <Gauge className="w-48 h-48 text-blue-400" />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Disponibilidad Flota</div>
          <div className="text-2xl font-extrabold text-blue-400 mt-1">
            {twinState?.disponibilidad_flota_pct ?? 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Meta: &ge; 85.0%</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Equipos Operativos</div>
          <div className="text-2xl font-extrabold text-emerald-400 mt-1">
            {twinState?.equipos_operativos ?? 0} <span className="text-xs font-normal text-slate-400">/ {twinState?.equipos_total ?? 33}</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {twinState?.equipos_mantenimiento ?? 0} en mant. | {twinState?.equipos_fallados ?? 0} averiados
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Stockouts Activos</div>
          <div className="text-2xl font-extrabold text-rose-400 mt-1">
            {twinState?.stockouts_activos ?? 0}
          </div>
          <div className="text-[11px] text-rose-400/80 mt-1">Repuestos en cero</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Fill Rate Almacén</div>
          <div className="text-2xl font-extrabold text-indigo-400 mt-1">
            {twinState?.fill_rate_pct ?? 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Stock &ge; Seguridad</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Downtime Acumulado</div>
          <div className="text-2xl font-extrabold text-amber-400 mt-1">
            {Number(twinState?.downtime_acumulado_horas ?? 0).toLocaleString()} <span className="text-xs font-normal text-slate-400">h</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Horas de parada flota</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-medium">Pérdida Producción</div>
          <div className="text-2xl font-extrabold text-slate-100 mt-1">
            ${(Number(twinState?.perdida_produccion_usd ?? 0) / 1000).toFixed(0)}k <span className="text-xs font-normal text-slate-400">USD</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">$14,500/h parada</div>
        </div>
      </div>

      {/* 3D Mine Topography & Equipment BOM Inspector Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* 3D Visualizer */}
        <div className="lg:col-span-7">
          <Mine3DViewer
            fleet={fleet}
            selectedCode={selectedEquipmentCode}
            onSelectEquipment={(code) => setSelectedEquipmentCode(code)}
          />
        </div>

        {/* Equipment BOM Inspector */}
        <div className="lg:col-span-5">
          {selectedEquipmentCode ? (
            <EquipmentInspector
              selectedCode={selectedEquipmentCode}
              onClose={() => setSelectedEquipmentCode('')}
              onStatusChanged={loadData}
            />
          ) : (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 space-y-3">
              <Eye className="w-10 h-10 text-blue-400 mx-auto opacity-70" />
              <div className="font-bold text-slate-200 text-sm">Selecciona un Equipo</div>
              <p className="text-xs text-slate-400 max-w-xs mx-auto">
                Haz clic sobre cualquier nodo de equipo en el visor 3D o en la lista inferior para inspeccionar su telemetría y su Bill of Materials (BOM).
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Snapshot Controller */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 font-bold text-slate-200">
            <Camera className="w-5 h-5 text-blue-400" />
            <span>Captura de Snapshot Digital</span>
          </div>
          <span className="text-xs text-slate-400">Guarda el estado completo del sistema para simular réplicas</span>
        </div>

        <form onSubmit={handleCaptureSnapshot} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
          <div className="md:col-span-4">
            <label className="text-xs text-slate-400 block mb-1">Nombre del Snapshot:</label>
            <input
              type="text"
              value={snapName}
              onChange={(e) => setSnapName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div className="md:col-span-5">
            <label className="text-xs text-slate-400 block mb-1">Notas de Contexto:</label>
            <input
              type="text"
              value={snapNotes}
              onChange={(e) => setSnapNotes(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="md:col-span-3">
            <button
              type="submit"
              disabled={snapSubmitting}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-50 text-sm shadow-md shadow-blue-600/20"
            >
              <Camera className="w-4 h-4" />
              {snapSubmitting ? 'Guardando...' : 'Congelar Snapshot'}
            </button>
          </div>
        </form>

        {snapSuccess && (
          <div className="mt-3 p-3 bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs rounded-lg flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> {snapSuccess}
          </div>
        )}
      </div>

      {/* Fleet Monitoring (33 Equipos) */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
              <Truck className="w-5 h-5 text-indigo-400" />
              Flota de Mina Subterránea (33 Equipos Pesados)
            </h3>
            <p className="text-xs text-slate-400">Salud calculada mediante modelo de desgaste Weibull (&beta;=2.2). Haz clic para inspeccionar.</p>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-lg border border-slate-700">
            {['ALL', 'OPERATIVO', 'MANTENIMIENTO', 'FALLADO'].map((f) => (
              <button
                key={f}
                onClick={() => setFleetFilter(f)}
                className={`px-3 py-1 rounded text-xs font-semibold transition ${
                  fleetFilter === f ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {f === 'ALL' ? 'Todos (33)' : f}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-[380px] overflow-y-auto pr-1">
          {filteredFleet.map((eq) => {
            const isOp = eq.estado === 'OPERATIVO';
            const isMant = eq.estado === 'MANTENIMIENTO';
            const isSelected = selectedEquipmentCode === eq.codigo;

            return (
              <button
                key={eq.id}
                onClick={() => setSelectedEquipmentCode(eq.codigo)}
                className={`text-left p-3.5 rounded-xl border transition cursor-pointer ${
                  isSelected
                    ? 'bg-blue-950/40 border-blue-500 shadow-md ring-1 ring-blue-500/50'
                    : 'bg-slate-800/60 border-slate-700/70 hover:border-slate-500 hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-sm text-slate-100">{eq.codigo}</span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      isOp
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : isMant
                        ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    }`}
                  >
                    {eq.estado}
                  </span>
                </div>

                <div className="text-xs font-medium text-slate-200 truncate">{eq.tipo}</div>
                <div className="text-[11px] text-slate-400">{eq.nombre}</div>

                <div className="mt-3">
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400">Salud Activo:</span>
                    <span className="font-bold text-slate-200">{eq.salud_pct}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        eq.salud_pct >= 70 ? 'bg-emerald-500' : eq.salud_pct >= 40 ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${eq.salud_pct}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-700/50">
                  <span>Horómetro: {eq.horas_operacion}h</span>
                  <span>Cota Z: {eq.posicion?.z}m</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Critical Spare Parts Inventory */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
        <h3 className="font-bold text-slate-100 text-base mb-3 flex items-center gap-2">
          <Package className="w-5 h-5 text-amber-400" />
          Almacén de Repuestos Críticos & Vulnerabilidad de Suministro (SDI)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 text-[11px] uppercase tracking-wider">
              <tr>
                <th className="p-3">Código</th>
                <th className="p-3">Repuesto</th>
                <th className="p-3">Categoría</th>
                <th className="p-3">Stock Actual</th>
                <th className="p-3">Stock Seguridad</th>
                <th className="p-3">Punto Reorden</th>
                <th className="p-3">Lead Time (días)</th>
                <th className="p-3">Proveedor Principal</th>
                <th className="p-3">Riesgo Monopólico</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {inventory.slice(0, 8).map((r) => (
                <tr key={r.repuesto_id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-mono font-bold text-slate-200">{r.repuesto_codigo}</td>
                  <td className="p-3 font-medium text-slate-100">{r.repuesto_nombre}</td>
                  <td className="p-3 text-slate-400">{r.categoria}</td>
                  <td className="p-3">
                    <span className={`font-bold ${r.stock_actual === 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {r.stock_actual}
                    </span>
                  </td>
                  <td className="p-3">{r.stock_seguridad}</td>
                  <td className="p-3">{r.punto_reorden}</td>
                  <td className="p-3">{r.lead_time_promedio} d</td>
                  <td className="p-3 text-slate-300 truncate max-w-[140px]">{r.dominant_supplier}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.single_source_risk === 'ALTO'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {r.single_source_risk === 'ALTO' ? 'PROVEEDOR ÚNICO' : 'DIVERSIFICADO'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
