// Detailed criteria assessment table with status pills and source audit triggers

import React from 'react';
import { StatusPill } from './StatusPill';
import type { CriterionAssessment } from '../types/api';
import { FileText, ArrowRight } from 'lucide-react';

interface EligibilityTableProps {
  assessments: CriterionAssessment[];
  onSelectEvidence: (assessment: CriterionAssessment) => void;
}

export const EligibilityTable: React.FC<EligibilityTableProps> = ({
  assessments,
  onSelectEvidence,
}) => {
  if (!assessments || assessments.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-zinc-500 italic bg-zinc-950/40 rounded-lg border border-zinc-800/60">
        No specific criteria assessments recorded for this candidate.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-950/70">
      <table className="w-full text-left border-collapse text-xs">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400 font-medium">
            <th className="py-2.5 px-3">Criterion</th>
            <th className="py-2.5 px-3">Required Value</th>
            <th className="py-2.5 px-3">Candidate Value</th>
            <th className="py-2.5 px-3">Status</th>
            <th className="py-2.5 px-3">Evaluation Details</th>
            <th className="py-2.5 px-3 text-right">Evidence</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
          {assessments.map((a, idx) => (
            <tr key={a.criterion_id || idx} className="hover:bg-zinc-900/30 transition-colors">
              <td className="py-2.5 px-3 font-medium text-zinc-200 whitespace-nowrap">
                {a.criterion}
              </td>
              <td className="py-2.5 px-3 text-zinc-400 max-w-[150px] truncate" title={a.required_value || ''}>
                {a.required_value || '—'}
              </td>
              <td className="py-2.5 px-3 text-zinc-400 max-w-[150px] truncate" title={a.student_value || ''}>
                {a.student_value || '—'}
              </td>
              <td className="py-2.5 px-3 whitespace-nowrap">
                <StatusPill status={a.status} size="sm" />
              </td>
              <td className="py-2.5 px-3 text-zinc-400 min-w-[200px]">
                <div>{a.reason}</div>
                {a.next_action && (
                  <div className="text-[11px] text-amber-300/90 mt-0.5 flex items-center gap-1">
                    <ArrowRight className="w-3 h-3 shrink-0" />
                    <span>{a.next_action}</span>
                  </div>
                )}
              </td>
              <td className="py-2.5 px-3 text-right whitespace-nowrap">
                {a.source_excerpt ? (
                  <button
                    onClick={() => onSelectEvidence(a)}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 text-[11px] font-medium transition-colors"
                  >
                    <FileText className="w-3 h-3 text-zinc-400" />
                    View Excerpt
                  </button>
                ) : (
                  <span className="text-zinc-600 text-[11px]">No excerpt</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
