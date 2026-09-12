import { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import SimulationBar from './components/SimulationBar';
import OverviewPage from './pages/OverviewPage';
import IssuesPage from './pages/IssuesPage';
import ExplorerPage from './pages/ExplorerPage';
import AskPage from './pages/AskPage';
import { useWebSocket, type WSMessage } from './useWebSocket';

function App() {
  const [activeIssueCount, setActiveIssueCount] = useState(3);
  const [simulationActive, setSimulationActive] = useState(false);
  const [ticketRate, setTicketRate] = useState(0);
  const [toasts, setToasts] = useState<{ id: string; title: string; desc: string; severity: string }[]>([]);

  const handleWsMessage = useCallback((msg: WSMessage) => {
    switch (msg.event) {
      case 'EMERGING_ISSUE_DETECTED': {
        const data = msg.data as {
          id: string;
          title: string;
          severity: string;
          volume_growth_pct: number;
          ticket_count: number;
        };

        const toast = {
          id: data.id as string,
          title: data.title,
          desc: `${data.ticket_count} tickets · +${Number(data.volume_growth_pct).toFixed(0)}% spike`,
          severity: data.severity as string,
        };
        setToasts((prev) => [...prev, toast]);
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== toast.id));
        }, 8000);

        setActiveIssueCount((prev) => prev + 1);
        break;
      }
      case 'SIMULATION_PROGRESS': {
        const data = msg.data as { injected: number; total: number };
        setSimulationActive(true);
        setTicketRate(5);
        if (Number(data.injected) >= Number(data.total)) {
          setSimulationActive(false);
          setTicketRate(0);
        }
        break;
      }
    }
  }, []);

  const handleMockSimulate = (scenarioId: string) => {
    const titleMap: Record<string, string> = {
      visa_outage: 'Visa Checkout Error Outage',
      login_bug: 'SSO Login Loop Bug (v4.2.0)',
      mobile_crash: 'Android 14 Launch Crash Spike',
      delivery_delay: 'EU Warehouse Dispatch Delay',
      subscription_issue: 'Double Billing Error Spike',
    };

    const title = titleMap[scenarioId] || 'New Emerging Issue Detected';
    const toast = {
      id: Date.now().toString(),
      title,
      desc: '150 tickets injected · +340% volume spike detected by pgvector',
      severity: 'CRITICAL',
    };

    setToasts((prev) => [...prev, toast]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== toast.id));
    }, 8000);

    setActiveIssueCount((prev) => prev + 1);
  };

  const { connected } = useWebSocket(handleWsMessage);

  return (
    <Router>
      <div className="app-layout">
        <Sidebar activeIssueCount={activeIssueCount} />

        <main className="main-content">
          <SimulationBar
            connected={connected}
            simulationActive={simulationActive}
            ticketRate={ticketRate}
            onMockSimulate={handleMockSimulate}
          />

          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/issues" element={<IssuesPage />} />
            <Route path="/explorer" element={<ExplorerPage />} />
            <Route path="/explorer/:issueId" element={<ExplorerPage />} />
            <Route path="/ask" element={<AskPage />} />
          </Routes>
        </main>

        {/* Toast Notifications */}
        <div className="toast-container">
          {toasts.map((toast) => (
            <div key={toast.id} className={`toast ${toast.severity.toLowerCase()}`}>
              <div>
                <div className="toast-title">{toast.title}</div>
                <div className="toast-desc">{toast.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Router>
  );
}

export default App;
