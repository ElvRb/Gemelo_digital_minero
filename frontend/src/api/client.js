const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('API unreachable');
    return res.json();
  },

  // Digital Twin
  async getDigitalTwinState() {
    const res = await fetch(`${API_BASE_URL}/digital-twin/state`);
    if (!res.ok) throw new Error('Failed to fetch Digital Twin state');
    return res.json();
  },

  async getDigitalTwinFleet() {
    const res = await fetch(`${API_BASE_URL}/digital-twin/fleet`);
    if (!res.ok) throw new Error('Failed to fetch fleet state');
    return res.json();
  },

  async getEquipmentBOM(codigo) {
    const res = await fetch(`${API_BASE_URL}/digital-twin/equipment/${codigo}/bom`);
    if (!res.ok) throw new Error('Failed to fetch equipment BOM');
    return res.json();
  },

  async toggleEquipmentStatus(codigo, nuevoEstado) {
    const res = await fetch(`${API_BASE_URL}/digital-twin/equipment/${codigo}/toggle-status?nuevo_estado=${nuevoEstado}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to toggle equipment status');
    return res.json();
  },

  async getDigitalTwinInventory() {
    const res = await fetch(`${API_BASE_URL}/digital-twin/inventory`);
    if (!res.ok) throw new Error('Failed to fetch inventory');
    return res.json();
  },

  async getDigitalTwinSnapshots() {
    const res = await fetch(`${API_BASE_URL}/digital-twin/snapshots`);
    if (!res.ok) throw new Error('Failed to fetch snapshots');
    return res.json();
  },

  async captureSnapshot(nombre, notas) {
    const res = await fetch(`${API_BASE_URL}/digital-twin/snapshot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, notas })
    });
    if (!res.ok) throw new Error('Failed to capture snapshot');
    return res.json();
  },

  // Simulation: System Dynamics
  async runSystemDynamics(params) {
    const res = await fetch(`${API_BASE_URL}/simulation/run-sd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to run System Dynamics simulation');
    return res.json();
  },

  // Simulation: Benchmark (Scenarios E0 - E3 vs Strategies P0 - P3)
  async runBenchmark(scenarioType = 'BASE', horizonDays = 365) {
    const res = await fetch(`${API_BASE_URL}/simulation/benchmark`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_type: scenarioType, horizon_days: horizonDays, random_seed: 42 })
    });
    if (!res.ok) throw new Error('Failed to run benchmark');
    return res.json();
  },

  // Simulation: Multi-Agent (SimPy ABM)
  async runABM(params) {
    const res = await fetch(`${API_BASE_URL}/simulation/run-abm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to run ABM simulation');
    return res.json();
  },

  // Hypothesis Testing
  async getHypothesis(scenario = 'BASE', strategy = 'ESTRATEGIA_C') {
    const res = await fetch(`${API_BASE_URL}/simulation/hypothesis?scenario=${scenario}&strategy=${strategy}`);
    if (!res.ok) throw new Error('Failed to evaluate hypothesis');
    return res.json();
  }
};
