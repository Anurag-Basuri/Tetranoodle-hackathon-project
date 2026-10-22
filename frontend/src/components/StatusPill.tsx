// Reusable accessible status pill component with distinct icons and colors

import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Clock,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import type {
  CriterionStatus,
  OverallEligibility,
  VerificationStatus,
  JobStatus,
} from '../types/api';

interface StatusPillProps {
  status: CriterionStatus | OverallEligibility | VerificationStatus | JobStatus | string;
  size?: 'sm' | 'md';
}

export const StatusPill: React.FC<StatusPillProps> = ({ status, size: _size = 'md' }) => {
  const s = String(status).toLowerCase();

  // 1. Overall Eligibility mappings
  if (s === 'meets_all_stated') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <CheckCircle2 className="w-3.5 h-3.5" />
        Meets all stated criteria
      </span>
    );
  }
  if (s === 'likely_eligible') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-500/10 text-sky-400 border border-sky-500/30">
        <CheckCircle2 className="w-3.5 h-3.5" />
        Likely eligible (verify flagged items)
      </span>
    );
  }
  if (s === 'needs_info') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3.5 h-3.5" />
        Needs more information
      </span>
    );
  }
  if (s === 'not_eligible') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <XCircle className="w-3.5 h-3.5" />
        Not eligible
      </span>
    );
  }

  // 2. Individual Criterion Status mappings
  if (s === 'meets') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/25">
        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
        Meets
      </span>
    );
  }
  if (s === 'likely_meets') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-teal-500/15 text-teal-300 border border-teal-500/25">
        <CheckCircle2 className="w-3 h-3 text-teal-400" />
        Likely meets
      </span>
    );
  }
  if (s === 'needs_review') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/25">
        <AlertTriangle className="w-3 h-3 text-amber-400" />
        Needs review
      </span>
    );
  }
  if (s === 'unknown') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-500/15 text-slate-300 border border-slate-500/25">
        <HelpCircle className="w-3 h-3 text-slate-400" />
        Unknown
      </span>
    );
  }
  if (s === 'does_not_meet') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-rose-500/15 text-rose-300 border border-rose-500/25">
        <XCircle className="w-3 h-3 text-rose-400" />
        Does not meet
      </span>
    );
  }

  // 3. Verification Status mappings
  if (s === 'verified') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-500/15 text-indigo-300 border border-indigo-500/25">
        <ShieldCheck className="w-3 h-3 text-indigo-400" />
        Official source verified
      </span>
    );
  }
  if (s === 'partial') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/25">
        <ShieldAlert className="w-3 h-3 text-amber-400" />
        Partially verified
      </span>
    );
  }
  if (s === 'unverified') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-500/15 text-slate-300 border border-slate-500/25">
        <HelpCircle className="w-3 h-3 text-slate-400" />
        Unverified discovery
      </span>
    );
  }
  if (s === 'conflict') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-rose-500/15 text-rose-300 border border-rose-500/25">
        <AlertTriangle className="w-3 h-3 text-rose-400" />
        Source conflict
      </span>
    );
  }

  // 4. Job lifecycle status
  if (s === 'running') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/15 text-blue-400 border border-blue-500/30 animate-pulse">
        <Clock className="w-3.5 h-3.5 animate-spin" />
        Agents researching
      </span>
    );
  }
  if (s === 'completed' || s === 'completed_with_warnings') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
        <CheckCircle2 className="w-3.5 h-3.5" />
        Report Ready
      </span>
    );
  }
  if (s === 'cancelled') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-500/15 text-slate-400 border border-slate-500/30">
        <Clock className="w-3.5 h-3.5" />
        Cancelled
      </span>
    );
  }
  if (s === 'failed') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30">
        <XCircle className="w-3.5 h-3.5" />
        Failed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-700 text-slate-300">
      {status}
    </span>
  );
};
