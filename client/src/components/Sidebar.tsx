import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, AlertTriangle, Search, MessageSquare, Activity
} from 'lucide-react';

interface SidebarProps {
  activeIssueCount: number;
}

export default function Sidebar({ activeIssueCount }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <Activity size={18} color="white" />
        </div>
        <div>
          <h1>Pulse</h1>
          <span>Incident Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={17} />
          Overview
        </NavLink>

        <NavLink
          to="/issues"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <AlertTriangle size={17} />
          Emerging Incidents
          {activeIssueCount > 0 && (
            <span className="nav-badge">{activeIssueCount}</span>
          )}
        </NavLink>

        <NavLink
          to="/explorer"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Search size={17} />
          Root Cause Explorer
        </NavLink>

        <NavLink
          to="/ask"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <MessageSquare size={17} />
          Copilot & Search
        </NavLink>
      </nav>

      <div style={{
        padding: '14px 20px',
        borderTop: '1px solid var(--border-primary)',
        fontSize: '11px',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)'
      }}>
        Pulse v2.4 · Enterprise
      </div>
    </aside>
  );
}
