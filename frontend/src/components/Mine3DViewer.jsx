import React, { useMemo } from 'react';
import Plotly from 'plotly.js-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot = createPlotlyComponent(Plotly);
import { Eye, Layers, Compass } from 'lucide-react';

export default function Mine3DViewer({ fleet = [], onSelectEquipment, selectedCode }) {
  const plotData = useMemo(() => {
    // 1. Subterranean Depth Levels (Mesh3d Planes)
    const levels = [
      { name: 'Nivel -120m (Taller Superficie)', z: -120.0, color: 'rgba(51, 65, 85, 0.25)' },
      { name: 'Nivel -240m (Producción Norte)', z: -240.0, color: 'rgba(30, 58, 138, 0.25)' },
      { name: 'Nivel -360m (Estación Bombeo)', z: -360.0, color: 'rgba(6, 78, 59, 0.25)' },
      { name: 'Nivel -480m (Galería Avance)', z: -480.0, color: 'rgba(120, 53, 15, 0.25)' }
    ];

    const traces = [];

    levels.forEach((lvl) => {
      traces.push({
        type: 'mesh3d',
        x: [-250, 400, 400, -250],
        y: [-200, -200, 320, 320],
        z: [lvl.z, lvl.z, lvl.z, lvl.z],
        color: lvl.color,
        opacity: 0.35,
        name: lvl.name,
        showlegend: false,
        hoverinfo: 'skip'
      });
    });

    // 2. Main Extraction Shaft (Pique Vertical 0 a -480m)
    const zShaft = Array.from({ length: 50 }, (_, i) => -(i * 480) / 49);
    const xShaft = new Array(50).fill(0);
    const yShaft = new Array(50).fill(0);

    traces.push({
      type: 'scatter3d',
      mode: 'lines',
      x: xShaft,
      y: yShaft,
      z: zShaft,
      line: { color: '#64748b', width: 6, dash: 'dash' },
      name: 'Pique Vertical Central',
      hoverinfo: 'text',
      text: 'Pique Vertical Central de Extracción y Ventilación (0m a -480m)',
      showlegend: false
    });

    // 3. Equipment Nodes grouped by status
    const statusConfig = {
      OPERATIVO: { color: '#10b981', symbol: 'circle', size: 9 },
      MANTENIMIENTO: { color: '#f59e0b', symbol: 'circle', size: 10 },
      FALLADO: { color: '#ef4444', symbol: 'diamond', size: 13 },
      FUERA_DE_SERVICIO: { color: '#94a3b8', symbol: 'square', size: 8 }
    };

    Object.entries(statusConfig).forEach(([status, cfg]) => {
      const subset = fleet.filter((eq) => eq.estado === status);
      if (subset.length === 0) return;

      const xs = subset.map((e) => e.posicion?.x ?? 0);
      const ys = subset.map((e) => e.posicion?.y ?? 0);
      const zs = subset.map((e) => e.posicion?.z ?? -120);
      const codes = subset.map((e) => e.codigo);
      const hoverTexts = subset.map(
        (e) =>
          `<b>${e.codigo} — ${e.nombre}</b><br>` +
          `Tipo: ${e.tipo}<br>` +
          `Estado: ${e.estado}<br>` +
          `Salud: ${e.salud_pct}%<br>` +
          `MTBF: ${e.mtbf_horas} h | MTTR: ${e.mttr_horas} h<br>` +
          `Coordenadas: (${e.posicion?.x}m, ${e.posicion?.y}m, Z=${e.posicion?.z}m)<br>` +
          `<i>Haz clic para inspeccionar BOM y telemetría</i>`
      );

      // Marker borders: highlight selected code
      const borderColors = subset.map((e) => (e.codigo === selectedCode ? '#60a5fa' : '#0f172a'));
      const borderWidths = subset.map((e) => (e.codigo === selectedCode ? 3 : 1));
      const sizes = subset.map((e) => (e.codigo === selectedCode ? cfg.size + 4 : cfg.size));

      traces.push({
        type: 'scatter3d',
        mode: 'markers+text',
        x: xs,
        y: ys,
        z: zs,
        marker: {
          size: sizes,
          color: cfg.color,
          symbol: cfg.symbol,
          line: { color: borderColors, width: borderWidths }
        },
        text: codes,
        textposition: 'top center',
        textfont: { size: 10, color: '#f1f5f9' },
        hovertext: hoverTexts,
        hoverinfo: 'text',
        name: `${status} (${subset.length})`
      });
    });

    return traces;
  }, [fleet, selectedCode]);

  const layout = useMemo(
    () => ({
      autosize: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      showlegend: false,
      scene: {
        xaxis: {
          title: 'Este (m)',
          color: '#94a3b8',
          gridcolor: '#1e293b',
          backgroundcolor: '#0b1120',
          showbackground: true
        },
        yaxis: {
          title: 'Norte (m)',
          color: '#94a3b8',
          gridcolor: '#1e293b',
          backgroundcolor: '#0b1120',
          showbackground: true
        },
        zaxis: {
          title: 'Cota Profundidad Z (m)',
          color: '#94a3b8',
          gridcolor: '#1e293b',
          backgroundcolor: '#0b1120',
          showbackground: true
        },
        aspectmode: 'manual',
        aspectratio: { x: 1.2, y: 1.2, z: 0.85 },
        camera: {
          eye: { x: 1.6, y: -1.6, z: 1.1 }
        }
      },
      margin: { l: 0, r: 0, b: 0, t: 0 }
    }),
    []
  );

  const handleClick = (e) => {
    if (e.points && e.points[0]) {
      const point = e.points[0];
      if (point.text) {
        onSelectEquipment(point.text);
      }
    }
  };

  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 overflow-hidden relative">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-2 px-1">
        <div>
          <h3 className="font-bold text-slate-100 text-sm flex items-center gap-2">
            <Compass className="w-4 h-4 text-blue-400" />
            Topología Subterránea 3D de la Mina (Digital Twin 3D)
          </h3>
          <p className="text-[11px] text-slate-400">
            Vista espacial de 4 niveles (-120m a -480m), pique de extracción y ubicación en tiempo real de los 33 equipos.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Operativo
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Mantenimiento
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rotate-45 bg-rose-500 inline-block" /> Fallado
          </span>
        </div>
      </div>

      <div className="w-full h-[450px] rounded-lg overflow-hidden border border-slate-900 bg-slate-950">
        <Plot
          data={plotData}
          layout={layout}
          config={{ displayModeBar: true, displaylogo: false, responsive: true }}
          onClick={handleClick}
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      <div className="text-[11px] text-slate-500 mt-2 px-1 flex items-center justify-between">
        <span>💡 Puedes rotar con clic izquierdo, hacer zoom con rueda y trasladar con clic derecho.</span>
        <span>Haz clic sobre cualquier equipo para abrir su inspector digital.</span>
      </div>
    </div>
  );
}
