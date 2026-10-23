// Navigation bar with clean typography and understated controls

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { GraduationCap, GitBranch } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const lastJobId = localStorage.getItem('scholarpilot_last_job_id');

  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200">
            <GraduationCap className="w-4 h-4 text-zinc-300" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-zinc-100 tracking-tight">ScholarPilot</span>
            <span className="text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.2 rounded">
              research
            </span>
          </div>
        </Link>

        {/* Navigation links */}
        <nav className="flex items-center gap-3 sm:gap-4">
          <Link
            to="/"
            className={`text-xs font-medium px-2.5 py-1.5 rounded-md transition-colors ${
              location.pathname === '/'
                ? 'bg-zinc-800/80 text-zinc-100'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            New Intake
          </Link>

          {lastJobId && (
            <Link
              to={`/jobs/${lastJobId}`}
              className={`text-xs font-medium px-2.5 py-1.5 rounded-md transition-colors ${
                location.pathname.startsWith('/jobs')
                  ? 'bg-zinc-800/80 text-zinc-100'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Latest Report
            </Link>
          )}

          <div className="hidden sm:flex items-center gap-1.5 pl-3 border-l border-zinc-800 text-xs text-zinc-400 font-normal">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Operational</span>
          </div>

          <a
            href="https://github.com/Anurag-Basuri/Tetranoodle-hackathon-project"
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 rounded-md transition-colors"
            title="GitHub Repository"
          >
            <GitBranch className="w-4 h-4" />
          </a>
        </nav>
      </div>
    </header>
  );
};
