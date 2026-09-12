import { useState, useEffect } from 'react';
import { Sliders, Square } from 'lucide-react';
import { API, apiFetch } from '../api';

interface SimulationBarProps {
  connected: boolean;
  simulationActive: boolean;
  ticketRate: number;
  onMockSimulate?: (scenarioId: string) => void;
}

const SCENARIOS = [
  { id: 'visa_outage', label: 'Visa Checkout Failure' },
  { id: 'login_bug', label: 'SSO Auth Loop' },
  { id: 'mobile_crash', label: 'Android Launch Crash' },
  { id: 'delivery_delay', label: 'EU Warehouse Latency' },
  { id: 'subscription_issue', label: 'Double Billing Spike' },
];

export default function SimulationBar({ connected, simulationActive, ticketRate, onMockSimulate }: SimulationBarProps) {
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [localActive, setLocalActive] = useState(false);

  const triggerScenario = async (scenarioId: string) => {
    setLoading(true);
    setRunningScenario(scenarioId);
    try {
      await apiFetch(API.triggerSimulation(), {
        method: 'POST',
        body: JSON.stringify({ scenario: scenarioId, speed: 5, ticket_count: 150 }),
      });
      if (!connected) {
        setLocalActive(true);
        if (onMockSimulate) onMockSimulate(scenarioId);
      }
    } catch (err) {
      console.error('Failed to trigger simulation:', err);
    } finally {
      setLoading(false);
    }
  };

  const stopScenario = async () => {
    if (!runningScenario) return;
    try {
      await apiFetch(API.stopSimulation(runningScenario), { method: 'POST' });
    } catch (err) {
      console.error('Failed to stop simulation:', err);
    } finally {
      setRunningScenario(null);
      setLocalActive(false);
    }
  };

  const isActive = simulationActive || localActive;

  useEffect(() => {
    if (localActive) {
      const timer = setTimeout(() => {
        setLocalActive(false);
        setRunningScenario(null);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [localActive]);

  return (
    <div className="sim-bar">
      <div className="sim-bar-label">
        <Sliders size={13} />
        Incident Simulator
      </div>

      <div className={`sim-bar-dot ${isActive ? 'active' : ''}`} />

      <div className="sim-bar-status">
        {isActive
          ? `INJECTING TRAFFIC (${connected ? ticketRate : 5} tix/s)`
          : connected
            ? 'STREAMING ACTIVE'
            : 'READY (STANDBY)'
        }
      </div>

      <div className="sim-bar-buttons">
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            className={`sim-btn ${runningScenario === s.id ? 'active' : ''}`}
            onClick={() => runningScenario === s.id ? stopScenario() : triggerScenario(s.id)}
            disabled={loading || (runningScenario !== null && runningScenario !== s.id)}
          >
            {runningScenario === s.id ? (
              <><Square size={10} /> Stop</>
            ) : (
              <>{s.label}</>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
