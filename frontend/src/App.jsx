import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DigitalTwinView from './components/DigitalTwinView';
import SystemDynamicsView from './components/SystemDynamicsView';
import ResilienceLabView from './components/ResilienceLabView';
import MultiAgentView from './components/MultiAgentView';

export default function App() {
  const [activeTab, setActiveTab] = useState('twin');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen w-screen bg-[#090d16] text-slate-100 flex flex-col font-sans overflow-hidden">
      <Navbar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          isOpen={sidebarOpen} 
          setIsOpen={setSidebarOpen} 
        />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 bg-[#090d16] w-full">
          <div className="max-w-7xl mx-auto space-y-6 pb-12">
            {activeTab === 'twin' && <DigitalTwinView />}
            {activeTab === 'sd' && <SystemDynamicsView />}
            {activeTab === 'resilience' && <ResilienceLabView />}
            {activeTab === 'abm' && <MultiAgentView />}
          </div>
        </main>
      </div>
    </div>
  );
}
