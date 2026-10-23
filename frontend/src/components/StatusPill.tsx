// Accessible status badges with quiet, high-legibility tones

import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ShieldCheck,
  ShieldAlert,
  Loader2,
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

export const StatusPill: React.FC<StatusPillProps> = ({ status }) => {
  const s = String(status).toLowerCase();

  // Overall Eligibility
  if (s === 'meets_all_stated') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-950/40 text-emerald-300 border border-emerald-800/50">
        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
        Meets all stated criteria
      </span>
    );
  }
  if (s === 'likely_eligible') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-sky-950/40 text-sky-300 border border-sky-800/50">
        <CheckCircle2 className="w-3 h-3 text-sky-400" />
        Likely eligible (verify flagged items)
      </span>
    );
  }
  if (s === 'needs_info') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/40 text-amber-300 border border-amber-800/50">
        <AlertTriangle className="w-3 h-3 text-amber-400" />
        Needs more information
      </span>
    );
  }
  if (s === 'not_eligible') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-rose-950/40 text-rose-300 border border-rose-800/50">
        <XCircle className="w-3 h-3 text-rose-400" />
        Not eligible
      </span>
    );
  }

  // Individual Criterion Status
  if (s === 'meets') {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-emerald-950/40 text-emerald-300 border border-emerald-800/50">
        <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
        Meets
      </span>
    );
  }
  if (s === 'likely_meets') {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-teal-950/40 text-teal-300 border border-teal-800/50">
        <CheckCircle2 className="w-2.5 h-2.5 text-teal-400" />
        Likely meets
      </span>
    );
  }
  if (s === 'needs_review') {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-amber-950/40 text-amber-300 border border-amber-800/50">
        <AlertTriangle className="w-2.5 h-2.5 text-amber-400" />
        Needs review
      </span>
    );
  }
  if (s === 'unknown') {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-zinc-800/80 text-zinc-400 border border-zinc-700/60">
        <HelpCircle className="w-2.5 h-2.5 text-zinc-400" />
        Unknown
      </span>
    );
  }
  if (s === 'does_not_meet') {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-rose-950/40 text-rose-300 border border-rose-800/50">
        <XCircle className="w-2.5 h-2.5 text-rose-400" />
        Does not meet
      </span>
    );
  }

  // Verification Status
  if (s === 'verified') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800/80 text-zinc-300 border border-zinc-700">
        <ShieldCheck className="w-3 h-3 text-emerald-400" />
        Official source verified
      </span>
    );
  }
  if (s === 'partial') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/30 text-amber-300 border border-amber-800/40">
        <ShieldAlert className="w-3 h-3 text-amber-400" />
        Partially verified
      </span>
    );
  }
  if (s === 'unverified') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800/60 text-zinc-400 border border-zinc-700/50">
        <HelpCircle className="w-3 h-3 text-zinc-500" />
        Unverified source
      </span>
    );
  }

  // Job lifecycle status
  if (s === 'running') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-blue-950/40 text-blue-300 border border-blue-800/50">
        <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
        Research in progress
      </span>
    );
  }
  if (s === 'completed' || s === 'completed_with_warnings') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-950/40 text-emerald-300 border border-emerald-800/50">
        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
        Report ready
      </span>
    );
  }
  if (s === 'cancelled') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">
        Cancelled
      </span>
    );
  }
  if (s === 'failed') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-rose-950/40 text-rose-300 border border-rose-800/50">
        <XCircle className="w-3 h-3 text-rose-400" />
        Failed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
      {status}
    </span>
  );
};
