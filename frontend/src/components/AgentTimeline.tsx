// Multi-agent pipeline visualizer and execution log stream

import React from 'react';
import {
  UserCheck,
  Search,
  ShieldCheck,
  CheckSquare,
  Award,
  Terminal,
  Check,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import type { JobEvent, JobStatus } from '../types/api';

interface AgentTimelineProps {
  events: JobEvent[];
  jobStatus: JobStatus;
}

interface AgentStage {
  id: string;
  step: number;
  name: string;
  role: string;
  icon: React.ElementType;
}

const STAGES: AgentStage[] = [
  { id: 'profile_analyst', step: 1, name: 'Profile Analyst', role: 'Records & GitHub', icon: UserCheck },
  { id: 'opportunity_scout', step: 2, name: 'Opportunity Scout', role: 'Discovery (≥12)', icon: Search },
  { id: 'verification_agent', step: 3, name: 'Verification Agent', role: 'Official sources', icon: ShieldCheck },
  { id: 'eligibility_analyst', step: 4, name: 'Eligibility Analyst', role: 'Rules & gaps', icon: CheckSquare },
  { id: 'ranking_application_agent', step: 5, name: 'Ranking & SOP', role: '6-Factor scoring', icon: Award },
];

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ events, jobStatus }) => {
  const getStageStatus = (agentId: string) => {
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
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 sm:p-5 space-y-4">
      {/* Pipeline Header */}
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/80">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">Research Pipeline</h2>
          <p className="text-xs text-zinc-400">Cooperative agent workflow across five specialized stages</p>
        </div>
        <div className="text-xs font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
          {events.length} events
        </div>
      </div>

      {/* 5 Pipeline stages */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
        {STAGES.map((stage) => {
          const status = getStageStatus(stage.id);
          const Icon = stage.icon;

          let cardBorder = 'border-zinc-800 bg-zinc-900/40 text-zinc-400';
          let statusBadge = (
            <span className="w-4 h-4 rounded-full border border-zinc-700 flex items-center justify-center text-[10px] text-zinc-500 font-mono">
              {stage.step}
            </span>
          );

          if (status === 'active') {
            cardBorder = 'border-blue-700/60 bg-blue-950/20 text-blue-200';
            statusBadge = <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />;
          } else if (status === 'completed') {
            cardBorder = 'border-zinc-800 bg-zinc-900/60 text-zinc-300';
            statusBadge = (
              <span className="w-4 h-4 rounded-full bg-emerald-950 border border-emerald-800/80 flex items-center justify-center">
                <Check className="w-2.5 h-2.5 text-emerald-400" />
              </span>
            );
          } else if (status === 'error') {
            cardBorder = 'border-rose-900/60 bg-rose-950/20 text-rose-300';
            statusBadge = <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
          }

          return (
            <div
              key={stage.id}
              className={`p-3 rounded-lg border transition-colors ${cardBorder}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <Icon className="w-4 h-4 text-zinc-400" />
                {statusBadge}
              </div>
              <div className="text-xs font-medium text-zinc-200 leading-tight">{stage.name}</div>
              <div className="text-[11px] text-zinc-400 mt-0.5">{stage.role}</div>
            </div>
          );
        })}
      </div>

      {/* Execution Logs Terminal */}
      <div className="bg-zinc-950 rounded-lg border border-zinc-800/80 p-3">
        <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-zinc-900 text-[11px] font-mono text-zinc-400">
          <Terminal className="w-3 h-3 text-zinc-400" />
          <span>Execution Stream</span>
        </div>
        <div className="max-h-40 overflow-y-auto space-y-1.5 font-mono text-[11px] pr-1">
          {events.length === 0 ? (
            <div className="text-zinc-500 italic py-2 text-center text-xs">Awaiting events...</div>
          ) : (
            events.slice(-20).map((evt) => {
              let tagColor = 'text-zinc-400';
              if (evt.level === 'info') tagColor = 'text-blue-400';
              if (evt.level === 'success') tagColor = 'text-emerald-400';
              if (evt.level === 'warning') tagColor = 'text-amber-400';
              if (evt.level === 'error') tagColor = 'text-rose-400';

              return (
                <div key={evt.seq} className="flex items-start gap-2 leading-relaxed">
                  <span className="text-zinc-600 shrink-0 select-none">
                    {new Date(evt.at).toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span className={`shrink-0 font-medium ${tagColor}`}>
                    [{evt.agent.replace('_', ' ')}]
                  </span>
                  <span className="text-zinc-300">{evt.message}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
