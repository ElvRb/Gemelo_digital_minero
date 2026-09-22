import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, User, Database, RefreshCw, Menu, X } from 'lucide-react';
import { api } from '../api/client';

export default function Navbar({ sidebarOpen, setSidebarOpen }) {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.getHealth();
        setApiStatus('online');
      } catch (err) {
        setApiStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50 px-4 sm:px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {/* Toggle Button (Visible on Tablet/Mobile) */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle Menu"
          className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition lg:hidden"
        >
          {sidebarOpen ? <X className="w-5 h-5 text-blue-400" /> : <Menu className="w-5 h-5" />}
        </button>

        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/20 shrink-0">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base sm:text-lg font-bold text-slate-100 tracking-tight">MINING DIGITAL TWIN</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 hidden sm:inline-block">
              Core Científico
            </span>
          </div>
          <p className="text-[11px] sm:text-xs text-slate-400 truncate max-w-[200px] sm:max-w-none">
            Resiliencia y Simulación de Cadena de Suministro Subterránea
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        {/* API Health Pill */}
        <div className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-medium">
          <span className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
          <span className={apiStatus === 'online' ? 'text-emerald-300' : 'text-rose-300'}>
            FastAPI: <span className="hidden sm:inline">{apiStatus === 'online' ? 'Conectado (8000)' : 'Desconectado'}</span>
          </span>
        </div>

        {/* User Card */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs">
            SC
          </div>
          <div className="text-left hidden md:block">
            <div className="text-xs font-semibold text-slate-200 leading-none">Sofia Contreras</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Administrador</div>
          </div>
        </div>
      </div>
    </header>
  );
}
