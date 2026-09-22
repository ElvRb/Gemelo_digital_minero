import React from 'react';
import { Layers, Activity, ShieldAlert, Cpu, Sparkles, LogOut, X, User } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, isOpen, setIsOpen }) {
  const navItems = [
    {
      id: 'twin',
      label: 'Gemelo Digital',
      subtitle: 'Topología 3D, Flota & BOM',
      icon: Layers,
    },
    {
      id: 'sd',
      label: 'Dinámica de Sistemas',
      subtitle: 'Stocks, Flujos & Retardos No Lineales',
      icon: Activity,
    },
    {
      id: 'resilience',
      label: 'Laboratorio de Resiliencia',
      subtitle: 'Escenarios E0-E3 & Políticas P0-P3',
      icon: ShieldAlert,
    },
    {
      id: 'abm',
      label: 'Simulación Multi-Agente',
      subtitle: 'SimPy ABM & Evaluación H0 vs H1',
      icon: Cpu,
    }
  ];

  const handleSelect = (id) => {
    setActiveTab(id);
    if (setIsOpen) {
      setIsOpen(false);
    }
  };

  return (
    <>
      {/* Tablet & Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 z-50
          transition-transform duration-300 ease-in-out
          fixed inset-y-0 left-0 w-72 h-full
          lg:static lg:translate-x-0 lg:h-full lg:w-72
          ${isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Top Header */}
        <div className="p-4 pb-2 border-b border-slate-800/80 shrink-0">
          <div className="flex items-center justify-between px-2 py-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              📋 Menú Principal
            </span>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-md text-slate-400 hover:text-white lg:hidden"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Scrollable Navigation Items */}
        <div className="flex-1 overflow-y-auto p-3.5 space-y-2.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => handleSelect(item.id)}
                className={`w-full text-left p-3 rounded-xl transition-all flex items-start gap-3.5 border ${
                  isActive
                    ? 'bg-blue-600/20 border-blue-500/50 text-blue-300 shadow-md shadow-blue-500/10'
                    : 'bg-slate-800/40 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700'
                }`}
              >
                <div
                  className={`p-2 rounded-lg shrink-0 ${
                    isActive ? 'bg-blue-500 text-white shadow-sm' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <div className={`font-semibold text-sm leading-snug ${isActive ? 'text-blue-200 font-bold' : 'text-slate-200'}`}>
                    {item.label}
                  </div>
                  <div className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    {item.subtitle}
                  </div>
                </div>
              </button>
            );
          })}

          <div className="pt-2">
            <div className="p-3 rounded-xl bg-gradient-to-r from-blue-950/40 to-indigo-950/40 border border-blue-800/30 text-xs text-slate-300 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-blue-400 text-[11px]">
                <Sparkles className="w-3.5 h-3.5" /> Gemelo Digital Subterráneo
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Sincronización física de 33 equipos, BOM e integración de Dinámica de Sistemas (SD + ABM).
              </p>
            </div>
          </div>
        </div>

        {/* Permanently Pinned Bottom Section: User Profile & Cerrar Sesión */}
        <div className="p-4 border-t border-slate-800/90 bg-slate-900/95 shrink-0 space-y-3">
          {/* User Profile Card */}
          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center font-bold text-white text-xs shadow shrink-0">
              SC
            </div>
            <div className="truncate min-w-0">
              <div className="text-xs font-bold text-slate-100 truncate">Sofia Contreras</div>
              <div className="text-[11px] text-blue-400 font-medium">Administrador</div>
              <div className="text-[10px] text-slate-400 truncate">admin@minera.com</div>
            </div>
          </div>

          {/* Cerrar Sesión Button */}
          <button
            onClick={() => {
              if (window.confirm('¿Deseas cerrar la sesión de Sofia Contreras?')) {
                window.location.reload();
              }
            }}
            className="w-full flex items-center justify-center gap-2 p-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 hover:text-rose-200 border border-rose-500/30 text-xs font-bold transition shadow-sm"
          >
            <LogOut className="w-4 h-4 text-rose-400" />
            <span>🚪 Cerrar Sesión</span>
          </button>
        </div>
      </aside>
    </>
  );
}
