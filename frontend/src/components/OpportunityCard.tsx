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
    <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-colors space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
              #{item.rank} Match
            </span>
            <StatusPill status={item.overall} />
            <StatusPill status={opp.verification_status} size="sm" />
            {opp.country && (
              <span className="inline-flex items-center gap-1 text-[11px] text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                <Globe className="w-3 h-3 text-zinc-500" />
                {opp.country}
              </span>
            )}
          </div>

          <h3 className="text-base font-semibold text-zinc-100">
            {opp.name}
          </h3>

          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <GraduationCap className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-zinc-300">{opp.institution || 'Awarding Body'}</span>
            {opp.official_url && (
              <>
                <span className="text-zinc-600">•</span>
                <a
                  href={opp.official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-zinc-400 hover:text-zinc-200 inline-flex items-center gap-1 underline underline-offset-2 transition-colors"
                >
                  Official Page
                  <ExternalLink className="w-3 h-3" />
                </a>
              </>
            )}
          </div>
        </div>

        {/* Score & Action */}
        <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2.5 shrink-0 pt-1">
          <div className="text-right">
            <div className="text-[11px] text-zinc-400 uppercase tracking-wider">Score</div>
            <div className="text-xl font-semibold text-zinc-100 font-mono">
              {item.score.toFixed(1)}
              <span className="text-xs text-zinc-500 font-normal"> / 100</span>
            </div>
          </div>

          <button
            onClick={() => onDraftSop(opp.id)}
            disabled={isDrafting}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
          >
            <FileEdit className="w-3.5 h-3.5" />
            {isDrafting ? 'Drafting...' : 'Draft SOP'}
          </button>
        </div>
      </div>

      {/* Rationale and Details */}
      <div className="bg-zinc-950/60 rounded-lg p-3 border border-zinc-800/80 text-xs text-zinc-300 space-y-1.5">
        <p className="leading-relaxed">
          <span className="font-medium text-zinc-200">Evaluation: </span>
          {item.rationale}
        </p>

        {item.trade_offs && item.trade_offs.length > 0 && (
          <div className="text-zinc-400 text-[11px]">
            <span className="font-medium text-amber-400">Trade-offs: </span>
            {item.trade_offs.join(' • ')}
          </div>
        )}

        {item.next_actions && item.next_actions.length > 0 && (
          <div className="text-zinc-400 text-[11px]">
            <span className="font-medium text-blue-400">Next Action: </span>
            {item.next_actions.join(' • ')}
          </div>
        )}
      </div>

      {/* 6-Factor Score Breakdown */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-zinc-400">
          <span className="font-medium">Score Breakdown (100 pts max)</span>
          <span className="text-zinc-500">Documented Weights §9.4</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs font-mono">
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Funding (25)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.funding_fit} pts</div>
          </div>
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Academic (25)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.academic_fit} pts</div>
          </div>
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Relevance (20)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.program_relevance} pts</div>
          </div>
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Country (10)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.country_preference} pts</div>
          </div>
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Deadline (10)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.deadline_feasibility} pts</div>
          </div>
          <div className="bg-zinc-950/40 p-2 rounded border border-zinc-800/60">
            <div className="text-[10px] text-zinc-500">Evidence (10)</div>
            <div className="font-medium text-zinc-200 mt-0.5">{breakdown.evidence_confidence} pts</div>
          </div>
        </div>
      </div>

      {/* Meta Row: Funding & Deadline */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-zinc-800/80 text-xs text-zinc-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <Banknote className="w-3.5 h-3.5 text-zinc-500" />
            <span>Funding: </span>
            <span className="font-medium capitalize text-zinc-200">{opp.funding_type.replace('_', ' ')}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
            <span>Deadline: </span>
            <span className="font-medium text-zinc-200">{opp.deadline || 'Ongoing / Unspecified'}</span>
          </div>
        </div>

        {/* Expand / Collapse Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-xs font-medium text-zinc-300 hover:text-white transition-colors"
        >
          <span>{expanded ? 'Hide Criteria' : `View ${item.assessments?.length || 0} Criteria`}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Expandable Criteria Table */}
      {expanded && (
        <div className="pt-2">
          <EligibilityTable
            assessments={item.assessments}
            onSelectEvidence={onSelectEvidence}
          />
        </div>
      )}
    </div>
  );
};
