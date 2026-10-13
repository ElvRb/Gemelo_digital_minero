import React, { useMemo, useState, useCallback, useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot = createPlotlyComponent(Plotly);
import { 
  Compass, Eye, EyeOff, Maximize2, Minimize2, RotateCcw, 
  Layers, Mountain, Crosshair, Wrench, ShieldAlert, CheckCircle2, 
  AlertTriangle, Truck, Info, Sparkles, Filter, Activity, Zap,
  Image as ImageIcon, ArrowRight, Gauge, Radio, X
} from 'lucide-react';
import mineRender from '../assets/mine_digital_twin_3d.jpg';

const SCHEMATIC_HOTSPOTS = [
  {
    id: 'surface',
    title: 'Superficie, Bocamina & Castillete (4,200 msnm)',
    desc: 'Bocamina de acceso portal 3850m, torre de izaje (headframe 48m), winche y planta de beneficio.',
    x: '61%',
    y: '14%',
    level: 'ALL',
    badge: 'SUPERFICIE'
  },
  {
    id: 'shaft',
    title: 'Pique Vertical Central (0m a -480m)',
    desc: 'Pique principal de extracción con skip de mineral y jaula de tránsito de personal hacia los 4 niveles.',
    x: '61%',
    y: '48%',
    level: 'ALL',
    badge: 'PIQUE 480m'
  },
  {
    id: 'ramp',
    title: 'Rampa Espiral Helicoidal de Transporte',
    desc: 'Declive helicoidal continuo con gradiente -12%. Circulación de camiones de bajo perfil y Scooptrams LHD.',
    x: '48%',
    y: '44%',
    level: 'ALL',
    badge: 'RAMPA -12%'
  },
  {
    id: 'l120',
    title: 'Nivel -120m: Almacén e Infraestructura',
    desc: 'Taller superficial de repuestos críticos, compresores estacionarios Atlas Copco y stock de insumos.',
    x: '24%',
    y: '40%',
    level: -120,
    badge: 'NIVEL -120m'
  },
  {
    id: 'l240',
    title: 'Nivel -240m: Producción Norte (Scooptram ST-04)',
    desc: 'Frente activo de carguío y acarreo con Scooptrams R1700K, taller subterráneo y faja CV-101.',
    x: '27%',
    y: '53%',
    level: -240,
    badge: 'NIVEL -240m'
  },
  {
    id: 'l360',
    title: 'Nivel -360m: Extracción y Bombeo (Jumbo DJ-07)',
    desc: 'Estación de bombas centrífugas Sulzer MSD, faja triturador CV-202 y cámara de ventilación axial Alphair.',
    x: '68%',
    y: '68%',
    level: -360,
    badge: 'NIVEL -360m'
  },
  {
    id: 'l480',
    title: 'Nivel -480m: Avance Profundo & Caserón 40',
    desc: 'Frente de perforación de tiros largos Simba S7, explotación Sublevel Stoping y sumidero de drenaje.',
    x: '75%',
    y: '80%',
    level: -480,
    badge: 'NIVEL -480m'
  }
];

export default function Mine3DViewer({ fleet = [], onSelectEquipment, selectedCode }) {
  const containerRef = useRef(null);

  // Mode: 'INTERACTIVE' (WebGL 3D Orbit) or 'SCHEMATIC' (High-res 3D Cross-section)
  const [viewMode, setViewMode] = useState('INTERACTIVE');
  const [activeHotspot, setActiveHotspot] = useState(null);

  // Viewer state
  const [selectedLevel, setSelectedLevel] = useState('ALL'); // 'ALL' | -120 | -240 | -360 | -480
  const [colorMode, setColorMode] = useState('STATUS'); // 'STATUS' | 'HEALTH' | 'TYPE'
  const [showLabels, setShowLabels] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showLayersMenu, setShowLayersMenu] = useState(false);

  // Layer toggles
  const [layers, setLayers] = useState({
    surface: true,
    spiralRamp: true,
    tunnels: true,
    shafts: true,
    stopes: true,
    waypoints: true,
    equipment: true,
  });

  const toggleLayer = (layerName) => {
    setLayers((prev) => ({ ...prev, [layerName]: !prev[layerName] }));
  };

  // Fullscreen toggle handler with HTML5 API and state fallback
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      setIsFullscreen(true);
      if (containerRef.current && containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen().catch(() => {});
      }
    } else {
      setIsFullscreen(false);
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
    }
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 150);
  };

  // Listen for fullscreen change (e.g. user presses Esc)
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isNowFullscreen = !!document.fullscreenElement;
      setIsFullscreen(isNowFullscreen);
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 150);
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        toggleFullscreen();
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isFullscreen]);

  // Camera presets
  const initialCamera = useMemo(
    () => ({
      eye: { x: 1.65, y: -1.65, z: 1.15 },
      center: { x: 0.1, y: 0.05, z: -0.35 },
      up: { x: 0, y: 0, z: 1 }
    }),
    []
  );

  const [camera, setCamera] = useState(initialCamera);

  const setCameraPreset = (type) => {
    if (type === 'ISO') {
      setCamera({
        eye: { x: 1.65, y: -1.65, z: 1.15 },
        center: { x: 0.1, y: 0.05, z: -0.35 },
        up: { x: 0, y: 0, z: 1 }
      });
    } else if (type === 'TOP') {
      setCamera({
        eye: { x: 0.001, y: 0.001, z: 2.6 },
        center: { x: 0.05, y: 0.05, z: -0.3 },
        up: { x: 0, y: 1, z: 0 }
      });
    } else if (type === 'SIDE') {
      setCamera({
        eye: { x: 2.6, y: 0.01, z: 0.1 },
        center: { x: 0.05, y: 0.05, z: -0.4 },
        up: { x: 0, y: 0, z: 1 }
      });
    } else if (type === 'FRONT') {
      setCamera({
        eye: { x: 0.01, y: -2.6, z: 0.1 },
        center: { x: 0.05, y: 0.05, z: -0.4 },
        up: { x: 0, y: 0, z: 1 }
      });
    } else if (type === 'FOCUS' && selectedEquipment) {
      const pos = selectedEquipment.posicion || { x: 0, y: 0, z: -240 };
      const nx = (pos.x || 0) / 400;
      const ny = (pos.y || 0) / 400;
      const nz = (pos.z || -240) / 480;
      setCamera({
        eye: { x: nx + 0.7, y: ny - 0.7, z: nz + 0.5 },
        center: { x: nx, y: ny, z: nz },
        up: { x: 0, y: 0, z: 1 }
      });
    }
  };

  // Find currently selected equipment
  const selectedEquipment = useMemo(() => {
    return fleet.find((e) => e.codigo === selectedCode) || null;
  }, [fleet, selectedCode]);

  // When selected equipment changes, focus
  const focusSelected = useCallback(() => {
    if (selectedEquipment) {
      setCameraPreset('FOCUS');
    }
  }, [selectedEquipment]);

  // ----------------------------------------------------
  // GENERATE 3D GEOMETRY TRACES (WEBGL)
  // ----------------------------------------------------
  const plotData = useMemo(() => {
    const traces = [];

    // Helper: Level visibility filter
    const isLevelVisible = (z) => {
      if (selectedLevel === 'ALL') return true;
      return Math.abs(z - Number(selectedLevel)) < 40;
    };

    // 1. SURFACE RELIEF & ANDEAN MOUNTAIN TOPOGRAPHY (Z = +20m to +85m)
    if (layers.surface && selectedLevel === 'ALL') {
      const xRange = [];
      const yRange = [];
      const step = 45;
      for (let x = -260; x <= 420; x += step) xRange.push(x);
      for (let y = -240; y <= 330; y += step) yRange.push(y);

      const zGrid = [];
      for (let j = 0; j < yRange.length; j++) {
        const row = [];
        const y = yRange[j];
        for (let i = 0; i < xRange.length; i++) {
          const x = xRange[i];
          const peak = 45 * Math.exp(-((x - 80) ** 2 + (y - 70) ** 2) / 45000);
          const ridge = 25 * Math.exp(-((x + 120) ** 2 + (y - 180) ** 2) / 35000);
          const undulation = 8 * Math.sin(x / 70) * Math.cos(y / 70);
          const baseAlt = 25;
          row.push(baseAlt + peak + ridge + undulation);
        }
        zGrid.push(row);
      }

      traces.push({
        type: 'surface',
        x: xRange,
        y: yRange,
        z: zGrid,
        colorscale: [
          [0.0, 'rgba(15, 23, 42, 0.45)'],
          [0.35, 'rgba(30, 41, 59, 0.40)'],
          [0.7, 'rgba(51, 65, 85, 0.35)'],
          [1.0, 'rgba(71, 85, 105, 0.45)']
        ],
        opacity: 0.38,
        showscale: false,
        name: 'Relieve Superficie Cordillera (4,200 msnm)',
        hoverinfo: 'text',
        hovertext: 'Topografía de Superficie — Macizo Rocoso Andino (Cota 0m a +85m)',
        contours: {
          z: {
            show: true,
            usecolormap: false,
            color: '#38bdf8',
            width: 1.2,
            project: { z: false }
          }
        }
      });
    }

    // 2. SURFACE PORTAL & HEADFRAME STRUCTURE (Torre de Pique / Castillete a Z=+45m)
    if (layers.shafts && (selectedLevel === 'ALL' || selectedLevel === -120)) {
      const hfX = [0, -18, -18, 0, 18, 18, 0, 0, -18, 18, 0];
      const hfY = [0, -18, 18, 0, 18, -18, 0, 0, 18, -18, 0];
      const hfZ = [48, 0, 0, 48, 0, 0, 48, 0, 0, 0, 48];

      traces.push({
        type: 'scatter3d',
        mode: 'lines',
        x: hfX,
        y: hfY,
        z: hfZ,
        line: { color: '#94a3b8', width: 4 },
        name: 'Castillete de Pique Superficie',
        hoverinfo: 'text',
        text: 'Castillete Minero de Superficie (Torre de Izaje y Winche 48m)',
        showlegend: false
      });

      traces.push({
        type: 'scatter3d',
        mode: 'markers',
        x: [0],
        y: [0],
        z: [48],
        marker: { size: 6, color: '#38bdf8', symbol: 'circle' },
        name: 'Polea Principal Winche',
        hoverinfo: 'text',
        text: 'Polea de Cable de Izaje (Headframe Sheave)',
        showlegend: false
      });
    }

    // 3. SUBTERRANEAN DEPTH PLANES / FOOTPRINT SLABS
    const levelsConfig = [
      { name: 'Nivel -120m (Taller Superficie y Almacén)', z: -120.0, color: 'rgba(51, 65, 85, 0.20)', borderColor: '#475569' },
      { name: 'Nivel -240m (Producción Norte y Taller Mecánico)', z: -240.0, color: 'rgba(30, 58, 138, 0.22)', borderColor: '#3b82f6' },
      { name: 'Nivel -360m (Estación Principal Bombeo y Ventilación)', z: -360.0, color: 'rgba(6, 78, 59, 0.22)', borderColor: '#10b981' },
      { name: 'Nivel -480m (Galería de Avance y Fondo de Mina)', z: -480.0, color: 'rgba(120, 53, 15, 0.22)', borderColor: '#f59e0b' }
    ];

    levelsConfig.forEach((lvl) => {
      if (!isLevelVisible(lvl.z)) return;

      traces.push({
        type: 'mesh3d',
        x: [-240, 390, 390, -240],
        y: [-190, -190, 310, 310],
        z: [lvl.z, lvl.z, lvl.z, lvl.z],
        color: lvl.color,
        opacity: selectedLevel === 'ALL' ? 0.35 : 0.65,
        name: lvl.name,
        showlegend: false,
        hoverinfo: 'skip'
      });

      traces.push({
        type: 'scatter3d',
        mode: 'lines',
        x: [-240, 390, 390, -240, -240],
        y: [-190, -190, 310, 310, -190],
        z: [lvl.z, lvl.z, lvl.z, lvl.z, lvl.z],
        line: { color: lvl.borderColor, width: 2, dash: 'dot' },
        name: `Límite ${lvl.name}`,
        hoverinfo: 'text',
        text: `Plano Horizontal ${lvl.name}`,
        showlegend: false
      });
    });

    // 4. VERTICAL EXTRACTION SHAFT & RAISE-BORING (Pique Central 0m a -480m)
    if (layers.shafts) {
      const zShaft = Array.from({ length: 49 }, (_, i) => -(i * 480) / 48);
      const xShaft = new Array(49).fill(0);
      const yShaft = new Array(49).fill(0);

      traces.push({
        type: 'scatter3d',
        mode: 'lines',
        x: xShaft,
        y: yShaft,
        z: zShaft,
        line: { color: '#38bdf8', width: 6, dash: 'solid' },
        name: 'Pique Central de Extracción',
        hoverinfo: 'text',
        text: 'Pique Vertical Central de Extracción de Mineral y Personal (0m a -480m)',
        showlegend: false
      });

      const stationZ = [-120, -240, -360, -480];
      stationZ.forEach((sz) => {
        if (!isLevelVisible(sz)) return;
        const circleSteps = 16;
        const ringX = [];
        const ringY = [];
        const ringZ = [];
        for (let i = 0; i <= circleSteps; i++) {
          const theta = (i / circleSteps) * 2 * Math.PI;
          ringX.push(18 * Math.cos(theta));
          ringY.push(18 * Math.sin(theta));
          ringZ.push(sz);
        }
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: ringX,
          y: ringY,
          z: ringZ,
          line: { color: '#38bdf8', width: 3 },
          name: `Estación Pique Z=${sz}m`,
          hoverinfo: 'text',
          text: `Estación de Pique y Enlace Nivel ${sz}m`,
          showlegend: false
        });
      });

      if (selectedLevel === 'ALL' || selectedLevel === -360) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [-200, -200, -200, -200],
          y: [-90, -90, -90, -90],
          z: [0, -120, -240, -360],
          line: { color: '#06b6d4', width: 5, dash: 'dash' },
          name: 'Chimenea Ventilación Sur',
          hoverinfo: 'text',
          text: 'Chimenea de Ventilación Principal RB-01 (Inyección de Aire Forzado)',
          showlegend: false
        });
      }

      if (selectedLevel === 'ALL' || selectedLevel === -240 || selectedLevel === -360) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [240, 130],
          y: [80, -60],
          z: [-240, -360],
          line: { color: '#f59e0b', width: 5, dash: 'dot' },
          name: 'Chimenea Ore Pass (Traspaso)',
          hoverinfo: 'text',
          text: 'Ore Pass OP-01: Traspaso de Mineral de Caserones N-240 a Triturador N-360',
          showlegend: false
        });
      }
    }

    // 5. MAIN CONTINUOUS HELICAL ACCESS RAMP (0m a -480m)
    if (layers.spiralRamp) {
      const rampPoints = 90;
      const rx = [];
      const ry = [];
      const rz = [];
      const totalTurns = 4.2;

      for (let i = 0; i <= rampPoints; i++) {
        const t = (i / rampPoints) * totalTurns * 2 * Math.PI;
        const z = 5 - (485 * (i / rampPoints));
        if (isLevelVisible(z)) {
          const radius = 80 + 15 * Math.sin(t * 0.7);
          rx.push(radius * Math.cos(t) + 30);
          ry.push(radius * Math.sin(t) + 20);
          rz.push(z);
        } else if (rx.length > 0 && rx[rx.length - 1] !== null) {
          rx.push(null);
          ry.push(null);
          rz.push(null);
        }
      }

      traces.push({
        type: 'scatter3d',
        mode: 'lines',
        x: rx,
        y: ry,
        z: rz,
        line: { color: '#fbbf24', width: 6 },
        name: 'Rampa Espiral Principal',
        hoverinfo: 'text',
        text: 'Rampa de Acceso y Transporte Pesado (Pendiente -12%, Tráfico Scooptrams)',
        showlegend: false
      });
    }

    // 6. UNDERGROUND DRIFT NETWORKS & TUNNELS
    if (layers.tunnels) {
      if (isLevelVisible(-120)) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [0, 0, -10, 0, 20, 50, 110],
          y: [0, -25, -20, 0, 30, 45, 60],
          z: new Array(7).fill(-120),
          line: { color: '#64748b', width: 5 },
          name: 'Galerías Nivel -120m',
          hoverinfo: 'text',
          text: 'Galería de Acceso, Almacén Central y Estación Compresores N-120m',
          showlegend: false
        });
      }

      if (isLevelVisible(-240)) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [0, 70, 120, 150, 200, 260, 300, 340, 360],
          y: [0, 40, 40, 80, 50, 100, 120, 150, 165],
          z: new Array(9).fill(-240),
          line: { color: '#3b82f6', width: 5.5 },
          name: 'Galería Principal Producción N-240',
          hoverinfo: 'text',
          text: 'Galería Principal de Acarreo y Frente de Avance 240-Norte',
          showlegend: false
        });

        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [150, 180, 160, 140],
          y: [80, 90, 70, 65],
          z: new Array(4).fill(-240),
          line: { color: '#60a5fa', width: 4, dash: 'solid' },
          name: 'Crucero Taller Mecánico N-240',
          hoverinfo: 'text',
          text: 'Bahías de Mantenimiento Taller Mecánico Central Subterráneo N-240',
          showlegend: false
        });
      }

      if (isLevelVisible(-360)) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [0, 50, 80, 95, 110, 130],
          y: [0, -80, -110, -95, -70, -60],
          z: new Array(6).fill(-360),
          line: { color: '#10b981', width: 5.5 },
          name: 'Galería de Bombeo y Chancado N-360',
          hoverinfo: 'text',
          text: 'Cámara de Bombeo Principal Sulzer MSD y Faja CV-202 (N-360)',
          showlegend: false
        });

        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [0, -70, -140, -200, -215],
          y: [0, -40, -65, -90, -85],
          z: new Array(5).fill(-360),
          line: { color: '#059669', width: 5 },
          name: 'Galería Ventilación Axial Sur N-360',
          hoverinfo: 'text',
          text: 'Circuito de Inyección de Aire — Ventiladores Principales Alphair V-101/102',
          showlegend: false
        });
      }

      if (isLevelVisible(-480)) {
        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [0, -50, -80, -110, -140, -165],
          y: [0, 50, 180, 230, 260, 285],
          z: new Array(6).fill(-480),
          line: { color: '#f97316', width: 5.5 },
          name: 'Galería Avance Profundo N-480',
          hoverinfo: 'text',
          text: 'Galería de Avance y Frente de Perforación 480-Oeste (Nivel Fondo)',
          showlegend: false
        });

        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: [-110, -135],
          y: [230, 245],
          z: [-480, -480],
          line: { color: '#ea580c', width: 4 },
          name: 'Sumidero N-480',
          hoverinfo: 'text',
          text: 'Estocada de Sumidero y Bombas Flygt Sumergibles N-480',
          showlegend: false
        });
      }
    }

    // 7. SUBLEVEL MINING STOPES / CASERONES 3D
    if (layers.stopes && (selectedLevel === 'ALL' || selectedLevel === -240 || selectedLevel === -360)) {
      const createBoxMesh = (x0, x1, y0, y1, z0, z1, color, name, desc) => ({
        type: 'mesh3d',
        x: [x0, x1, x1, x0, x0, x1, x1, x0],
        y: [y0, y0, y1, y1, y0, y0, y1, y1],
        z: [z0, z0, z0, z0, z1, z1, z1, z1],
        i: [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j: [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k: [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color: color,
        opacity: 0.42,
        name: name,
        hoverinfo: 'text',
        hovertext: desc,
        showlegend: false
      });

      traces.push(
        createBoxMesh(
          240, 280, 80, 115, -290, -245,
          '#f59e0b',
          'Caserón C-201 (Explotación)',
          '<b>Caserón de Explotación C-201</b><br>Método: Sublevel Stoping<br>Estado: Tronadura y Extracción Activa<br>Leyes: 2.4% Cu | 1.2 g/t Au'
        )
      );

      traces.push(
        createBoxMesh(
          295, 335, 115, 145, -290, -245,
          '#38bdf8',
          'Caserón C-202 (Relleno)',
          '<b>Caserón C-202</b><br>Estado: Relleno Hidráulico Cementado Completado<br>Soporte Geomecánico Activo'
        )
      );

      if (selectedLevel === 'ALL' || selectedLevel === -480) {
        traces.push(
          createBoxMesh(
            -155, -125, 235, 270, -475, -425,
            '#a855f7',
            'Caserón C-401 (En Preparación)',
            '<b>Caserón C-401 (Profundidad)</b><br>Estado: Perforación Tiros Largos Simba S7<br>Frente de Avance Masivo'
          )
        );
      }
    }

    // 8. STRATEGIC INFRASTRUCTURE WAYPOINTS
    if (layers.waypoints) {
      const waypoints = [
        { name: 'Bocamina Principal (Portal Nivel 0)', x: 0, y: 70, z: 15, tag: 'PORTAL', color: '#38bdf8' },
        { name: 'Almacén Central Superficie', x: 0, y: -25, z: -120, tag: 'ALMACÉN', color: '#94a3b8' },
        { name: 'Taller Mecánico Central N-240', x: 150, y: 80, z: -240, tag: 'TALLER', color: '#60a5fa' },
        { name: 'Frente de Avance 240-Norte', x: 340, y: 150, z: -240, tag: 'FRENTE', color: '#3b82f6' },
        { name: 'Estación Principal Bombeo N-360', x: 80, y: -110, z: -360, tag: 'BOMBEO', color: '#10b981' },
        { name: 'Cámara Ventilación Axial Sur N-360', x: -200, y: -90, z: -360, tag: 'VENTILACIÓN', color: '#06b6d4' },
        { name: 'Frente Perforación 480-Oeste', x: -140, y: 260, z: -480, tag: 'FRENTE', color: '#f97316' }
      ];

      const visibleWp = waypoints.filter((w) => isLevelVisible(w.z));

      if (visibleWp.length > 0) {
        traces.push({
          type: 'scatter3d',
          mode: showLabels ? 'markers+text' : 'markers',
          x: visibleWp.map((w) => w.x),
          y: visibleWp.map((w) => w.y),
          z: visibleWp.map((w) => w.z),
          marker: {
            size: 6,
            color: visibleWp.map((w) => w.color),
            symbol: 'square-open',
            line: { color: '#f8fafc', width: 2 }
          },
          text: showLabels ? visibleWp.map((w) => `📍 ${w.tag}`) : undefined,
          textposition: 'top right',
          textfont: { size: 9, color: '#93c5fd' },
          hovertext: visibleWp.map((w) => `<b>${w.name}</b><br>Coordenadas: (${w.x}m, ${w.y}m, ${w.z}m)`),
          hoverinfo: 'text',
          name: 'Zonas Estratégicas'
        });
      }
    }

    // 9. FLEET EQUIPMENT NODES (33 ASSETS)
    if (layers.equipment) {
      const visibleFleet = fleet.filter((eq) => isLevelVisible(eq.posicion?.z ?? -120));

      const categorySymbols = {
        'Scooptram (LHD)': 'circle',
        'Jumbo de Perforación': 'diamond',
        'Ventilador Axial Principal': 'square',
        'Bomba de Desagüe Multietapa': 'triangle-up',
        'Shovel / Pala de Carguío': 'hexagon',
        'Perforadora Long Hole': 'diamond',
        'Compresor Estacionario': 'cross',
        'Faja Transportadora (Conveyor)': 'hourglass'
      };

      const getStatusColor = (estado) => {
        if (estado === 'OPERATIVO') return '#10b981';
        if (estado === 'MANTENIMIENTO') return '#f59e0b';
        if (estado === 'FALLADO') return '#ef4444';
        return '#94a3b8';
      };

      const getHealthColor = (salud) => {
        if (salud >= 80) return '#10b981';
        if (salud >= 60) return '#84cc16';
        if (salud >= 40) return '#eab308';
        if (salud >= 20) return '#f97316';
        return '#ef4444';
      };

      const getTypeColor = (tipo) => {
        if (tipo.includes('Scooptram')) return '#38bdf8';
        if (tipo.includes('Jumbo')) return '#a855f7';
        if (tipo.includes('Bomba')) return '#06b6d4';
        if (tipo.includes('Ventilador')) return '#14b8a6';
        if (tipo.includes('Faja')) return '#eab308';
        if (tipo.includes('Pala') || tipo.includes('Shovel')) return '#f97316';
        if (tipo.includes('Compresor')) return '#ec4899';
        return '#8b5cf6';
      };

      const groups = {};

      visibleFleet.forEach((eq) => {
        let groupKey = eq.estado;
        if (colorMode === 'TYPE') groupKey = eq.tipo || 'OTRO';
        else if (colorMode === 'HEALTH') {
          groupKey = eq.salud_pct >= 70 ? 'ALTA_SALUD' : eq.salud_pct >= 40 ? 'MEDIA_SALUD' : 'CRITICA_SALUD';
        }

        if (!groups[groupKey]) groups[groupKey] = [];
        groups[groupKey].push(eq);
      });

      Object.entries(groups).forEach(([groupName, items]) => {
        const xs = items.map((e) => e.posicion?.x ?? 0);
        const ys = items.map((e) => e.posicion?.y ?? 0);
        const zs = items.map((e) => e.posicion?.z ?? -120);
        const codes = items.map((e) => e.codigo);
        const symbols = items.map((e) => categorySymbols[e.tipo] || 'circle');

        const colors = items.map((e) => {
          if (colorMode === 'HEALTH') return getHealthColor(e.salud_pct ?? 100);
          if (colorMode === 'TYPE') return getTypeColor(e.tipo || '');
          return getStatusColor(e.estado);
        });

        const borderColors = items.map((e) => (e.codigo === selectedCode ? '#60a5fa' : '#020617'));
        const borderWidths = items.map((e) => (e.codigo === selectedCode ? 3.5 : 1.2));
        const sizes = items.map((e) => (e.codigo === selectedCode ? 16 : 10.5));

        const hoverTexts = items.map(
          (e) =>
            `<span style="font-size:13px; font-weight:bold; color:#38bdf8;">${e.codigo} — ${e.nombre}</span><br>` +
            `<b style="color:#cbd5e1;">Tipo:</b> ${e.tipo}<br>` +
            `<b style="color:#cbd5e1;">Estado Físico:</b> <span style="color:${getStatusColor(e.estado)}; font-weight:bold;">${e.estado}</span><br>` +
            `<b style="color:#cbd5e1;">Salud Weibull:</b> ${e.salud_pct}% (h=${e.horas_operacion}h)<br>` +
            `<b style="color:#cbd5e1;">Confiabilidad MTBF:</b> ${e.mtbf_horas}h | MTTR: ${e.mttr_horas}h<br>` +
            `<b style="color:#cbd5e1;">Ubicación:</b> (${e.posicion?.x}m Este, ${e.posicion?.y}m Norte, Z=${e.posicion?.z}m)<br>` +
            `<i style="color:#93c5fd;">👉 Haz clic para abrir Despiece BOM y Telemetría</i>`
        );

        traces.push({
          type: 'scatter3d',
          mode: showLabels ? 'markers+text' : 'markers',
          x: xs,
          y: ys,
          z: zs,
          marker: {
            size: sizes,
            color: colors,
            symbol: symbols,
            line: { color: borderColors, width: borderWidths }
          },
          text: showLabels ? codes : undefined,
          textposition: 'top center',
          textfont: { size: 9.5, color: '#f8fafc' },
          hovertext: hoverTexts,
          hoverinfo: 'text',
          customdata: codes,
          name: `${groupName} (${items.length})`
        });
      });

      // 10. ACTIVE EQUIPMENT 3D LOCATOR BEACON & HALO
      if (selectedEquipment && isLevelVisible(selectedEquipment.posicion?.z ?? -120)) {
        const sx = selectedEquipment.posicion?.x ?? 0;
        const sy = selectedEquipment.posicion?.y ?? 0;
        const sz = selectedEquipment.posicion?.z ?? -120;

        const haloPoints = 24;
        const haloX = [];
        const haloY = [];
        const haloZ = [];
        const radius = 18;

        for (let i = 0; i <= haloPoints; i++) {
          const theta = (i / haloPoints) * 2 * Math.PI;
          haloX.push(sx + radius * Math.cos(theta));
          haloY.push(sy + radius * Math.sin(theta));
          haloZ.push(sz);
        }

        traces.push({
          type: 'scatter3d',
          mode: 'lines',
          x: haloX,
          y: haloY,
          z: haloZ,
          line: { color: '#60a5fa', width: 4.5 },
          name: 'Aura Selección 3D',
          hoverinfo: 'skip',
          showlegend: false
        });

        traces.push({
          type: 'scatter3d',
          mode: 'lines+markers',
          x: [sx, sx],
          y: [sy, sy],
          z: [sz + 35, sz],
          line: { color: '#38bdf8', width: 3, dash: 'dot' },
          marker: { size: [8, 0], color: '#38bdf8', symbol: ['cone', 'circle'] },
          name: 'Baliza Localizadora 3D',
          hoverinfo: 'skip',
          showlegend: false
        });
      }
    }

    return traces;
  }, [fleet, selectedCode, selectedEquipment, selectedLevel, colorMode, showLabels, layers]);

  // Layout configuration
  const layout = useMemo(
    () => ({
      autosize: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      showlegend: false,
      scene: {
        xaxis: {
          title: { text: 'Este X (m)', font: { size: 10, color: '#94a3b8' } },
          color: '#64748b',
          gridcolor: '#1e293b',
          backgroundcolor: '#070d18',
          showbackground: true,
          zerolinecolor: '#334155'
        },
        yaxis: {
          title: { text: 'Norte Y (m)', font: { size: 10, color: '#94a3b8' } },
          color: '#64748b',
          gridcolor: '#1e293b',
          backgroundcolor: '#070d18',
          showbackground: true,
          zerolinecolor: '#334155'
        },
        zaxis: {
          title: { text: 'Cota Z Profundidad (m)', font: { size: 10, color: '#94a3b8' } },
          color: '#64748b',
          gridcolor: '#1e293b',
          backgroundcolor: '#070d18',
          showbackground: true,
          zerolinecolor: '#334155',
          range: [-510, 90]
        },
        aspectmode: 'manual',
        aspectratio: { x: 1.3, y: 1.25, z: 0.95 },
        camera: camera
      },
      margin: { l: 0, r: 0, b: 0, t: 0 }
    }),
    [camera]
  );

  const handleClick = (e) => {
    if (e.points && e.points[0]) {
      const pt = e.points[0];
      const code = pt.customdata || pt.text;
      if (code && typeof code === 'string' && code.length <= 12 && onSelectEquipment) {
        onSelectEquipment(code);
      }
    }
  };

  const handleRelayout = (eventData) => {
    if (eventData && eventData['scene.camera']) {
      setCamera(eventData['scene.camera']);
    }
  };

  return (
    <div
      ref={containerRef}
      className={`bg-slate-950/95 border border-slate-800 rounded-2xl p-4 overflow-hidden relative shadow-2xl flex flex-col ${
        isFullscreen
          ? 'fixed inset-0 z-[99999] w-screen h-screen rounded-none p-4 bg-slate-950 border-none m-0'
          : 'w-full'
      }`}
    >
      {/* Top Header & Interactive Bar */}
      <div className="flex-shrink-0 flex flex-wrap items-center justify-between gap-3 mb-2.5 pb-2.5 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Compass className="w-4 h-4" />
            </span>
            <h3 className="font-extrabold text-slate-100 text-sm tracking-tight flex items-center gap-2">
              Gemelo Digital 3D — Mina Subterránea Titán Andino
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
                {viewMode === 'INTERACTIVE' ? 'Simulador WebGL 3D' : 'Corte Esquemático 3D'}
              </span>
            </h3>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            4 niveles subterráneos (-120m a -480m), rampa espiral de acarreo, pique central y posicionamiento en tiempo real de 33 activos.
          </p>
        </div>

        {/* View Mode & Visual Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Main View Mode Selector */}
          <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode('INTERACTIVE')}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition flex items-center gap-1.5 ${
                viewMode === 'INTERACTIVE'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Compass className="w-3.5 h-3.5" /> 3D Interactivo
            </button>
            <button
              onClick={() => setViewMode('SCHEMATIC')}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition flex items-center gap-1.5 ${
                viewMode === 'SCHEMATIC'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" /> Corte Esquemático 3D
            </button>
          </div>

          {viewMode === 'INTERACTIVE' && (
            <>
              {/* Diagnostic Mode Selector */}
              <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setColorMode('STATUS')}
                  title="Colorear por Estado Operativo"
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    colorMode === 'STATUS' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Estado
                </button>
                <button
                  onClick={() => setColorMode('HEALTH')}
                  title="Colorear por Degradación Weibull"
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    colorMode === 'HEALTH' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Salud
                </button>
                <button
                  onClick={() => setColorMode('TYPE')}
                  title="Colorear por Tipo de Maquinaria"
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition ${
                    colorMode === 'TYPE' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Tipo
                </button>
              </div>

              {/* Toggle Labels */}
              <button
                onClick={() => setShowLabels(!showLabels)}
                title={showLabels ? 'Ocultar Etiquetas 3D' : 'Mostrar Etiquetas 3D'}
                className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition ${
                  showLabels
                    ? 'bg-slate-800 border-slate-700 text-blue-400'
                    : 'bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300'
                }`}
              >
                {showLabels ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
              </button>

              {/* Layers Dropdown Toggle */}
              <div className="relative">
                <button
                  onClick={() => setShowLayersMenu(!showLayersMenu)}
                  className={`p-1.5 rounded-lg border text-xs flex items-center gap-1.5 transition ${
                    showLayersMenu
                      ? 'bg-blue-600/20 border-blue-500/40 text-blue-300'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-[11px] font-medium hidden sm:inline">Capas</span>
                </button>

                {showLayersMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-2.5 z-30 text-xs space-y-1.5 backdrop-blur-md">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 border-b border-slate-800">
                      Capas Estructurales 3D
                    </div>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Mountain className="w-3 h-3 text-slate-400" /> Relieve Superficie
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.surface}
                        onChange={() => toggleLayer('surface')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Sparkles className="w-3 h-3 text-amber-400" /> Rampa Espiral
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.spiralRamp}
                        onChange={() => toggleLayer('spiralRamp')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Compass className="w-3 h-3 text-blue-400" /> Red de Galerías
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.tunnels}
                        onChange={() => toggleLayer('tunnels')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Zap className="w-3 h-3 text-cyan-400" /> Piques y Chimeneas
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.shafts}
                        onChange={() => toggleLayer('shafts')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <ShieldAlert className="w-3 h-3 text-purple-400" /> Caserones 3D (Stopes)
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.stopes}
                        onChange={() => toggleLayer('stopes')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Activity className="w-3 h-3 text-emerald-400" /> Flota de Equipos (33)
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.equipment}
                        onChange={() => toggleLayer('equipment')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                    <label className="flex items-center justify-between px-2 py-1 rounded hover:bg-slate-800/80 cursor-pointer">
                      <span className="text-slate-300 flex items-center gap-1.5">
                        <Crosshair className="w-3 h-3 text-pink-400" /> Zonas Estratégicas
                      </span>
                      <input
                        type="checkbox"
                        checked={layers.waypoints}
                        onChange={() => toggleLayer('waypoints')}
                        className="accent-blue-600 rounded"
                      />
                    </label>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Fullscreen Toggle / Exit Button */}
          {isFullscreen ? (
            <button
              onClick={toggleFullscreen}
              className="px-3 py-1.5 rounded-lg bg-rose-600/20 text-rose-300 hover:bg-rose-600 hover:text-white border border-rose-500/40 text-xs font-bold flex items-center gap-1.5 transition shadow-lg shadow-rose-950/40"
            >
              <Minimize2 className="w-3.5 h-3.5" /> Salir de Pantalla Completa (Esc)
            </button>
          ) : (
            <button
              onClick={toggleFullscreen}
              title="Expandir a Pantalla Completa"
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Sub-bar: Level Filter & Quick Camera Presets (Only in Interactive View) */}
      {viewMode === 'INTERACTIVE' && (
        <div className="flex-shrink-0 flex flex-wrap items-center justify-between gap-2 mb-2 px-1">
          {/* Level Isolator Buttons */}
          <div className="flex items-center gap-1 overflow-x-auto text-xs py-0.5">
            <span className="text-[11px] text-slate-500 font-semibold mr-1 flex items-center gap-1">
              <Filter className="w-3 h-3" /> Nivel:
            </span>
            {[
              { id: 'ALL', label: 'Todos (-120m a -480m)' },
              { id: -120, label: '-120m (Taller/Almacén)' },
              { id: -240, label: '-240m (Producción Norte)' },
              { id: -360, label: '-360m (Bombeo/Vent)' },
              { id: -480, label: '-480m (Avance Fondo)' }
            ].map((lvl) => (
              <button
                key={lvl.id}
                onClick={() => setSelectedLevel(lvl.id)}
                className={`px-2 py-1 rounded-md text-[11px] font-semibold whitespace-nowrap transition border ${
                  selectedLevel === lvl.id
                    ? 'bg-blue-600/30 border-blue-500 text-blue-300 shadow-sm'
                    : 'bg-slate-900/60 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                {lvl.label}
              </button>
            ))}
          </div>

          {/* Camera Presets */}
          <div className="flex items-center gap-1 bg-slate-900/80 p-0.5 rounded-lg border border-slate-800 text-[11px]">
            <span className="text-slate-500 text-[10px] uppercase font-bold px-1.5">Cámara:</span>
            <button
              onClick={() => setCameraPreset('ISO')}
              title="Vista 3D Isométrica Global"
              className="px-2 py-0.5 rounded hover:bg-slate-800 text-slate-300 font-medium transition"
            >
              Isométrica
            </button>
            <button
              onClick={() => setCameraPreset('TOP')}
              title="Vista de Planta (Corte Superior Ortogonal)"
              className="px-2 py-0.5 rounded hover:bg-slate-800 text-slate-300 font-medium transition"
            >
              Planta
            </button>
            <button
              onClick={() => setCameraPreset('SIDE')}
              title="Vista Lateral / Perfil Transversal de Cotas"
              className="px-2 py-0.5 rounded hover:bg-slate-800 text-slate-300 font-medium transition"
            >
              Perfil
            </button>
            {selectedEquipment && (
              <button
                onClick={focusSelected}
                title={`Centrar cámara en ${selectedCode}`}
                className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 font-semibold transition flex items-center gap-1"
              >
                <Crosshair className="w-3 h-3 text-blue-400" /> {selectedCode}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main View Area (Flexibly occupies 100% remaining space in fullscreen or fixed in normal) */}
      <div
        className={`w-full rounded-xl overflow-hidden border border-slate-800/80 bg-slate-950 relative flex items-center justify-center ${
          isFullscreen ? 'flex-1 min-h-0' : 'h-[540px]'
        }`}
      >
        {viewMode === 'INTERACTIVE' ? (
          <div className="w-full h-full relative">
            <Plot
              data={plotData}
              layout={layout}
              config={{
                displayModeBar: true,
                displaylogo: false,
                responsive: true,
                modeBarButtonsToRemove: ['toImage', 'resetCameraLastSave3d']
              }}
              onClick={handleClick}
              onRelayout={handleRelayout}
              style={{ width: '100%', height: '100%' }}
            />

            {/* Floating Mini HUD: Selected Equipment Card */}
            {selectedEquipment && (
              <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-blue-500/50 rounded-xl p-3 shadow-2xl backdrop-blur-md max-w-sm pointer-events-auto z-10">
                <div className="flex items-center justify-between gap-3 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-black text-sm text-blue-400">{selectedEquipment.codigo}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.2 rounded-full border ${
                        selectedEquipment.estado === 'OPERATIVO'
                          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                          : selectedEquipment.estado === 'MANTENIMIENTO'
                          ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                      }`}
                    >
                      {selectedEquipment.estado}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Z={selectedEquipment.posicion?.z}m
                  </span>
                </div>

                <div className="text-xs font-semibold text-slate-100 truncate">{selectedEquipment.nombre}</div>
                <div className="text-[11px] text-slate-400 mb-2 truncate">
                  {selectedEquipment.tipo} &bull; Horómetro: {selectedEquipment.horas_operacion}h
                </div>

                <div className="flex items-center justify-between text-[11px] mb-1">
                  <span className="text-slate-400">Salud Weibull:</span>
                  <span className="font-bold text-slate-200">{selectedEquipment.salud_pct}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      selectedEquipment.salud_pct >= 70
                        ? 'bg-emerald-500'
                        : selectedEquipment.salud_pct >= 40
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${selectedEquipment.salud_pct}%` }}
                  />
                </div>
              </div>
            )}

            {/* Legend Overlay at Top Left */}
            <div className="absolute top-3 left-3 bg-slate-900/80 border border-slate-800/80 rounded-lg px-2.5 py-1.5 text-[11px] text-slate-300 pointer-events-none hidden sm:flex items-center gap-3 backdrop-blur-sm z-10">
              {colorMode === 'STATUS' && (
                <>
                  <span className="flex items-center gap-1 text-emerald-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> Operativo
                  </span>
                  <span className="flex items-center gap-1 text-amber-400">
                    <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> Mantenimiento
                  </span>
                  <span className="flex items-center gap-1 text-rose-400">
                    <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" /> Falla Activa
                  </span>
                </>
              )}
              {colorMode === 'HEALTH' && (
                <>
                  <span className="text-emerald-400">&ge;80% Excelente</span>
                  <span className="text-amber-400">40-79% Desgaste</span>
                  <span className="text-rose-400">&lt;40% Crítico</span>
                </>
              )}
              {colorMode === 'TYPE' && (
                <>
                  <span className="text-sky-400">&bull; Scooptrams</span>
                  <span className="text-purple-400">&bull; Jumbos</span>
                  <span className="text-cyan-400">&bull; Bombas</span>
                  <span className="text-teal-400">&bull; Ventiladores</span>
                </>
              )}
            </div>
          </div>
        ) : (
          /* SCHEMATIC 3D CROSS-SECTION HIGH-RES RENDER VIEW (Strict 16:9 Aspect to fit completely) */
          <div className="relative w-full h-full flex items-center justify-center p-2 overflow-hidden bg-slate-950">
            <div 
              className="relative max-h-full max-w-full flex items-center justify-center"
              style={{ aspectRatio: '16/9', width: '100%', maxHeight: '100%' }}
            >
              <img
                src={mineRender}
                alt="Corte Arquitectónico 3D del Gemelo Digital"
                className="w-full h-full object-contain rounded-xl select-none shadow-2xl border border-slate-800/80"
              />

              {/* Interactive Hotspots Overlaid on Image with absolute positioning */}
              {SCHEMATIC_HOTSPOTS.map((h) => {
                const isSelected = activeHotspot?.id === h.id;
                return (
                  <div
                    key={h.id}
                    style={{ left: h.x, top: h.y }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 group cursor-pointer z-20"
                    onClick={() => setActiveHotspot(isSelected ? null : h)}
                  >
                    <div className="relative flex items-center justify-center">
                      <span className="animate-ping absolute inline-flex h-6 w-6 rounded-full bg-cyan-400 opacity-60"></span>
                      <button
                        className={`relative w-6 h-6 rounded-full border flex items-center justify-center text-[11px] font-bold shadow-lg transition-transform transform group-hover:scale-125 ${
                          isSelected
                            ? 'bg-blue-500 border-white text-white ring-4 ring-blue-500/50'
                            : 'bg-slate-900/95 border-cyan-400 text-cyan-300 group-hover:bg-blue-600 group-hover:text-white'
                        }`}
                      >
                        +
                      </button>
                      <span className="absolute left-7 top-1/2 -translate-y-1/2 whitespace-nowrap bg-slate-900/95 border border-slate-700 text-slate-100 text-[10px] font-bold px-2 py-0.5 rounded shadow-lg pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-30">
                        {h.badge}
                      </span>
                    </div>
                  </div>
                );
              })}

              {/* Hotspot Detail Card Overlay */}
              {activeHotspot && (
                <div className="absolute top-4 right-4 max-w-xs sm:max-w-sm bg-slate-900/95 border border-blue-500/70 rounded-xl p-4 shadow-2xl backdrop-blur-md z-30 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      {activeHotspot.badge}
                    </span>
                    <button
                      onClick={() => setActiveHotspot(null)}
                      className="text-slate-400 hover:text-white text-sm font-bold w-6 h-6 rounded bg-slate-800 flex items-center justify-center"
                    >
                      &times;
                    </button>
                  </div>
                  <h4 className="text-sm font-bold text-white">{activeHotspot.title}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{activeHotspot.desc}</p>
                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                    <button
                      onClick={() => {
                        if (activeHotspot.level !== 'ALL') {
                          setSelectedLevel(activeHotspot.level);
                        }
                        setViewMode('INTERACTIVE');
                      }}
                      className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
                    >
                      Ver en Simulador 3D WebGL <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}

              {/* Floating Quick Action in bottom-right corner of image */}
              <div className="absolute bottom-3 right-3 z-20">
                <button
                  onClick={() => setViewMode('INTERACTIVE')}
                  className="px-3 py-1.5 rounded-lg bg-blue-600/90 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 transition shadow-lg shadow-blue-900/50 backdrop-blur-sm border border-blue-400/30"
                >
                  <Compass className="w-3.5 h-3.5" /> Abrir Simulador 3D WebGL
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Schematic Architectural Info Bar (Displayed cleanly outside/below the graphic) */}
      {viewMode === 'SCHEMATIC' && (
        <div className="flex-shrink-0 mt-2 px-3.5 py-2.5 bg-slate-900/90 border border-slate-800/80 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-4 sm:gap-6">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Método Explotación</span>
              <span className="font-semibold text-slate-100">Sublevel Stoping c/ Relleno</span>
            </div>
            <div className="border-l border-slate-800 pl-4 sm:pl-6">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Producción Diaria</span>
              <span className="font-bold text-emerald-400">6,500 TPD</span>
            </div>
            <div className="border-l border-slate-800 pl-4 sm:pl-6">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Profundidad Total</span>
              <span className="font-bold text-blue-400">480 metros (4 Niveles)</span>
            </div>
            <div className="border-l border-slate-800 pl-4 sm:pl-6">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Costo Parada Flota</span>
              <span className="font-bold text-amber-400">$14,500 USD / h</span>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span>Haz clic en los puntos <b className="text-cyan-400">(+)</b> del corte para inspeccionar cada nivel.</span>
          </div>
        </div>
      )}

      {/* Footer Info Tips (Only in interactive view) */}
      {viewMode === 'INTERACTIVE' && (
        <div className="flex-shrink-0 text-[11px] text-slate-500 mt-2 px-1 flex flex-wrap items-center justify-between gap-2">
          <span className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span>
              Interacción 3D: Clic izquierdo para rotar órbita &bull; Rueda para zoom &bull; Clic derecho para trasladar &bull; Clic en equipo para abrir BOM.
            </span>
          </span>
          <span className="font-mono text-slate-400 text-[10px]">
            Profundidad: 0m a -480m &bull; Activos en escena: {fleet.filter((eq) => selectedLevel === 'ALL' || Math.abs((eq.posicion?.z ?? -120) - Number(selectedLevel)) < 40).length} / 33
          </span>
        </div>
      )}
    </div>
  );
}
