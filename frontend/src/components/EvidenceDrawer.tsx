// Slide-over drawer displaying official source URL and verified excerpt

import React from 'react';
import { X, ExternalLink, ShieldCheck, Quote, Clock } from 'lucide-react';
import type { CriterionAssessment } from '../types/api';

interface EvidenceDrawerProps {
  assessment: CriterionAssessment | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ assessment, onClose }) => {
  if (!assessment) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-zinc-900 border-l border-zinc-800 h-full p-6 shadow-xl flex flex-col justify-between overflow-y-auto">
        <div className="space-y-5">
          {/* Header */}
          <div className="flex items-center justify-between pb-3.5 border-b border-zinc-800">
            <div className="flex items-center gap-2 text-zinc-200 font-medium text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Evidence Verification Audit</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Criterion Name */}
          <div>
            <span className="text-[11px] uppercase tracking-wider font-medium text-zinc-500">Criterion</span>
            <h3 className="text-base font-semibold text-zinc-100 mt-0.5">{assessment.criterion}</h3>
          </div>

          {/* Verification values */}
          <div className="grid grid-cols-2 gap-3 bg-zinc-950 p-3 rounded-lg border border-zinc-800 text-xs">
            <div>
              <span className="text-zinc-500 block text-[11px]">Required:</span>
              <span className="font-medium text-zinc-300">{assessment.required_value || 'None specified'}</span>
            </div>
            <div>
              <span className="text-zinc-500 block text-[11px]">Candidate:</span>
              <span className="font-medium text-zinc-300">{assessment.student_value || 'Not provided'}</span>
            </div>
          </div>

          {/* Verbatim Excerpt */}
          <div className="space-y-1.5">
            <span className="text-[11px] uppercase tracking-wider font-medium text-zinc-400 flex items-center gap-1.5">
              <Quote className="w-3.5 h-3.5 text-zinc-500" />
              Verbatim Source Excerpt (RapidFuzz ≥ 92%)
            </span>
            <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs leading-relaxed italic font-mono">
              "{assessment.source_excerpt || 'No excerpt available for this criterion'}"
            </div>
          </div>

          {/* Source Link */}
          {assessment.source_url && (
            <div className="space-y-1">
              <span className="text-[11px] uppercase tracking-wider font-medium text-zinc-500">Official URL</span>
              <a
                href={assessment.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-blue-400 hover:text-blue-300 hover:border-zinc-700 transition-colors break-all"
              >
                <ExternalLink className="w-3.5 h-3.5 shrink-0" />
                <span>{assessment.source_url}</span>
              </a>
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center gap-2 text-[11px] text-zinc-500 pt-2 border-t border-zinc-800/80">
            <Clock className="w-3 h-3" />
            <span>
              Verified on:{' '}
              {assessment.verified_at
                ? new Date(assessment.verified_at).toLocaleString()
                : 'Automated retrieval'}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-zinc-800 mt-6">
          <button
            onClick={onClose}
            className="w-full py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors"
          >
            Close Audit View
          </button>
        </div>
      </div>
    </div>
  );
};
