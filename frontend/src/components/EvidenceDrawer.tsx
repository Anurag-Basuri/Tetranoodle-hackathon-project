// Slide-over modal drawer displaying official source URL and verbatim excerpt

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
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/70 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-lg bg-slate-900 border-l border-slate-800 h-full p-6 shadow-2xl flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              <span>Evidence Verification Audit</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Criterion Name */}
          <div>
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">Evaluated Criterion</span>
            <h3 className="text-lg font-bold text-white mt-0.5">{assessment.criterion}</h3>
          </div>

          {/* Verification values */}
          <div className="grid grid-cols-2 gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 text-xs">
            <div>
              <span className="text-slate-500 block">Required Condition:</span>
              <span className="font-medium text-slate-200">{assessment.required_value || 'None specified'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Candidate Value:</span>
              <span className="font-medium text-slate-200">{assessment.student_value || 'Not provided'}</span>
            </div>
          </div>

          {/* Verbatim Excerpt */}
          <div className="space-y-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400 flex items-center gap-1.5">
              <Quote className="w-3.5 h-3.5 text-indigo-400" />
              Verbatim Source Excerpt (RapidFuzz ≥ 92%)
            </span>
            <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-indigo-200 text-xs leading-relaxed italic">
              "{assessment.source_excerpt || 'No excerpt available for this criterion'}"
            </div>
          </div>

          {/* Source Link */}
          {assessment.source_url && (
            <div className="space-y-1.5">
              <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">Official URL</span>
              <a
                href={assessment.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs text-sky-400 hover:text-sky-300 hover:border-sky-500/40 transition-colors break-all"
              >
                <ExternalLink className="w-4 h-4 shrink-0" />
                <span>{assessment.source_url}</span>
              </a>
            </div>
          )}

          {/* Verification metadata */}
          <div className="flex items-center gap-2 text-xs text-slate-500 pt-2 border-t border-slate-800/60">
            <Clock className="w-3.5 h-3.5" />
            <span>
              Verified on:{' '}
              {assessment.verified_at
                ? new Date(assessment.verified_at).toLocaleString()
                : 'Automated retrieval'}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-6 border-t border-slate-800 mt-6">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-slate-800 text-slate-200 hover:bg-slate-700 text-xs font-semibold transition-colors"
          >
            Close Audit View
          </button>
        </div>
      </div>
    </div>
  );
};
