// Ranked Opportunity Card featuring transparent 6-factor score and criteria drilldown

import React, { useState } from 'react';
import {
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Calendar,
  FileEdit,
  GraduationCap,
  Banknote,
  Globe,
  Award,
} from 'lucide-react';
import { StatusPill } from './StatusPill';
import { EligibilityTable } from './EligibilityTable';
import type { RankedOpportunity, CriterionAssessment } from '../types/api';

interface OpportunityCardProps {
  item: RankedOpportunity;
  onSelectEvidence: (a: CriterionAssessment) => void;
  onDraftSop: (oppId: string) => void;
  isDrafting?: boolean;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
  item,
  onSelectEvidence,
  onDraftSop,
  isDrafting,
}) => {
  const [expanded, setExpanded] = useState(false);
  const opp = item.opportunity;
  const breakdown = item.score_breakdown || {
    funding_fit: 0,
    academic_fit: 0,
    program_relevance: 0,
    country_preference: 0,
    deadline_feasibility: 0,
    evidence_confidence: 0,
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-sm transition-all hover:border-slate-700 space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          {/* Rank Badge */}
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 text-white font-bold text-sm flex items-center justify-center shrink-0 shadow-md shadow-indigo-500/20">
            #{item.rank}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <StatusPill status={item.overall} />
              <StatusPill status={opp.verification_status} size="sm" />
              {opp.country && (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-400 bg-slate-800/85 px-2 py-0.5 rounded-full border border-slate-700/60">
                  <Globe className="w-3 h-3 text-slate-500" />
                  {opp.country}
                </span>
              )}
            </div>

            <h3 className="text-base font-bold text-white group-hover:text-indigo-400 transition-colors">
              {opp.name}
            </h3>
            <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
              <GraduationCap className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-medium text-slate-300">{opp.institution || 'Awarding Body'}</span>
              {opp.official_url && (
                <a
                  href={opp.official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-0.5 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  Official Page
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Score & Action */}
        <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 shrink-0">
          <div className="text-right">
            <div className="text-xs text-slate-400 font-medium">Rank Score</div>
            <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-300 to-teal-300">
              {item.score.toFixed(1)}
              <span className="text-xs text-slate-500 font-normal">/100</span>
            </div>
          </div>

          <button
            onClick={() => onDraftSop(opp.id)}
            disabled={isDrafting}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50"
          >
            <FileEdit className="w-3.5 h-3.5" />
            {isDrafting ? 'Drafting SOP...' : 'Draft Grounded SOP'}
          </button>
        </div>
      </div>

      {/* Rationale and Next Actions */}
      <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/80 text-xs text-slate-300 space-y-2">
        <p className="leading-relaxed">
          <span className="font-semibold text-white">Ranking Rationale: </span>
          {item.rationale}
        </p>

        {item.trade_offs && item.trade_offs.length > 0 && (
          <div className="text-amber-400/90 text-[11px]">
            <span className="font-semibold text-amber-300">Trade-offs: </span>
            {item.trade_offs.join(' • ')}
          </div>
        )}

        {item.next_actions && item.next_actions.length > 0 && (
          <div className="text-sky-400/90 text-[11px]">
            <span className="font-semibold text-sky-300">Recommended Next Steps: </span>
            {item.next_actions.join(' • ')}
          </div>
        )}
      </div>

      {/* Transparent 6-Factor Score Breakdown */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span className="font-medium flex items-center gap-1">
            <Award className="w-3 h-3 text-indigo-400" />
            Transparent 6-Factor Score Breakdown
          </span>
          <span className="text-[10px] text-slate-500">Documented Weights §9.4</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Funding (25)</div>
            <div className="font-semibold text-emerald-400">{breakdown.funding_fit} pts</div>
          </div>
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Academic (25)</div>
            <div className="font-semibold text-indigo-400">{breakdown.academic_fit} pts</div>
          </div>
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Relevance (20)</div>
            <div className="font-semibold text-sky-400">{breakdown.program_relevance} pts</div>
          </div>
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Country (10)</div>
            <div className="font-semibold text-teal-400">{breakdown.country_preference} pts</div>
          </div>
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Deadline (10)</div>
            <div className="font-semibold text-amber-400">{breakdown.deadline_feasibility} pts</div>
          </div>
          <div className="bg-slate-950/40 p-2 rounded-lg border border-slate-800/60">
            <div className="text-[10px] text-slate-500">Evidence (10)</div>
            <div className="font-semibold text-purple-400">{breakdown.evidence_confidence} pts</div>
          </div>
        </div>
      </div>

      {/* Meta Bar: Funding & Deadline */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-xs text-slate-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <Banknote className="w-3.5 h-3.5 text-emerald-400" />
            <span>Funding: </span>
            <span className="font-semibold uppercase text-slate-200">{opp.funding_type.replace('_', ' ')}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-amber-400" />
            <span>Deadline: </span>
            <span className="font-semibold text-slate-200">{opp.deadline || 'Ongoing / Unspecified'}</span>
          </div>
        </div>

        {/* Expand / Collapse Criteria Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <span>{expanded ? 'Hide Criteria Audit' : `View ${item.assessments?.length || 0} Criteria`}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Expandable Criteria Table */}
      {expanded && (
        <div className="pt-2 animate-in fade-in duration-150">
          <EligibilityTable
            assessments={item.assessments}
            onSelectEvidence={onSelectEvidence}
          />
        </div>
      )}
    </div>
  );
};
