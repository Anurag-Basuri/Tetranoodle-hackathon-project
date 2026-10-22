// Five-lane multi-agent swarm progress visualizer and live event log

import React from 'react';
import {
  UserCheck,
  Search,
  ShieldCheck,
  CheckSquare,
  Award,
  Terminal,
  Clock,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import type { JobEvent, JobStatus } from '../types/api';

interface AgentTimelineProps {
  events: JobEvent[];
  jobStatus: JobStatus;
}

interface AgentLane {
  id: string;
  name: string;
  role: string;
  icon: React.ElementType;
}

const LANES: AgentLane[] = [
  { id: 'profile_analyst', name: 'Profile Analyst', role: 'Record Extraction & GitHub', icon: UserCheck },
  { id: 'opportunity_scout', name: 'Opportunity Scout', role: 'Search & Candidates (≥12)', icon: Search },
  { id: 'verification_agent', name: 'Verification Agent', role: 'Official Sources & RapidFuzz Quote', icon: ShieldCheck },
  { id: 'eligibility_analyst', name: 'Eligibility Analyst', role: 'Deterministic Rules & Gaps', icon: CheckSquare },
  { id: 'ranking_application_agent', name: 'Ranking & SOP Agent', role: '6-Factor Scoring & SOP Draft', icon: Award },
];

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ events, jobStatus }) => {
  // Derive status for each agent from emitted events
  const getAgentStatus = (agentId: string) => {
    if (jobStatus === 'completed' || jobStatus === 'completed_with_warnings') {
      return 'completed';
    }
    const agentEvents = events.filter((e) => e.agent === agentId);
    if (!agentEvents.length) {
      return jobStatus === 'running' ? 'waiting' : 'pending';
    }
    const lastEvent = agentEvents[agentEvents.length - 1];
    if (lastEvent.level === 'error') return 'error';
    if (lastEvent.type.includes('completed') || lastEvent.type.includes('verified')) return 'completed';
    return 'active';
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            Autonomous Agent Swarm
          </h2>
          <p className="text-xs text-slate-400">Cooperative parallel pipeline with isolated failure domains</p>
        </div>
        <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
          {events.length} events logged
        </span>
      </div>

      {/* 5-Lane agent grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {LANES.map((lane) => {
          const status = getAgentStatus(lane.id);
          const Icon = lane.icon;

          let badgeColor = 'bg-slate-800/60 border-slate-700 text-slate-400';
          let indicator = <Clock className="w-3.5 h-3.5 text-slate-500" />;

          if (status === 'active') {
            badgeColor = 'bg-indigo-950/40 border-indigo-500/50 text-indigo-300 ring-1 ring-indigo-500/30';
            indicator = <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />;
          } else if (status === 'completed') {
            badgeColor = 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300';
            indicator = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
          } else if (status === 'error') {
            badgeColor = 'bg-rose-950/30 border-rose-500/30 text-rose-300';
            indicator = <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
          }

          return (
            <div
              key={lane.id}
              className={`p-3.5 rounded-xl border transition-all ${badgeColor} relative overflow-hidden`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
                  <Icon className="w-4 h-4 text-indigo-400" />
                </div>
                <div className="flex items-center gap-1.5 text-[11px] font-medium">
                  {indicator}
                  <span className="capitalize">{status}</span>
                </div>
              </div>

              <div className="text-xs font-semibold text-white tracking-tight">{lane.name}</div>
              <div className="text-[11px] text-slate-400 mt-0.5 leading-snug">{lane.role}</div>
            </div>
          );
        })}
      </div>

      {/* Live chronological stream */}
      <div className="bg-slate-950/90 rounded-xl border border-slate-800/80 p-3.5">
        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-800 text-xs font-mono text-slate-400">
          <Terminal className="w-3.5 h-3.5 text-indigo-400" />
          <span>Real-Time Execution Logs</span>
        </div>
        <div className="max-h-48 overflow-y-auto space-y-2 font-mono text-xs pr-1">
          {events.length === 0 ? (
            <div className="text-slate-500 italic py-2 text-center">Awaiting swarm event stream...</div>
          ) : (
            events.slice(-15).map((evt) => {
              let badge = 'text-slate-400 bg-slate-800/50';
              if (evt.level === 'info') badge = 'text-sky-300 bg-sky-950/50 border border-sky-800/40';
              if (evt.level === 'success') badge = 'text-emerald-300 bg-emerald-950/50 border border-emerald-800/40';
              if (evt.level === 'warning') badge = 'text-amber-300 bg-amber-950/50 border border-amber-800/40';
              if (evt.level === 'error') badge = 'text-rose-300 bg-rose-950/50 border border-rose-800/40';

              return (
                <div key={evt.seq} className="flex items-start gap-2.5 text-[11px] leading-relaxed">
                  <span className="text-slate-500 shrink-0 select-none">
                    {new Date(evt.at).toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold shrink-0 ${badge}`}>
                    {evt.agent.replace('_', ' ')}
                  </span>
                  <span className="text-slate-300">{evt.message}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
