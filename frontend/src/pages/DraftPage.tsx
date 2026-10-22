// DraftPage for reviewing, copying, and exporting grounded Statement of Purpose drafts

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Copy,
  Check,
  Download,
  ArrowLeft,
  Sparkles,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';
import { useDraft } from '../api/hooks';

export const DraftPage: React.FC = () => {
  const { id: jobId, draftId } = useParams<{ id: string; draftId: string }>();
  const navigate = useNavigate();
  const { data: draft, isLoading } = useDraft(jobId, draftId);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!draft?.content) return;
    navigator.clipboard.writeText(draft.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!draft?.content) return;
    const blob = new Blob([draft.content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `SOP_Draft_${draft.opportunity_id.substring(0, 8)}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-400">
        <Sparkles className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-3" />
        <p className="text-sm">Retrieving grounded Statement of Purpose draft...</p>
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-400 space-y-3">
        <p className="text-sm">Draft not found or expired.</p>
        <button
          onClick={() => navigate(`/jobs/${jobId}`)}
          className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-semibold"
        >
          Back to Research Report
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Top back bar & actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-xl">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(`/jobs/${jobId}`)}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Back to Research Report"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-white">Statement of Purpose Draft</h1>
              <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[11px] font-semibold">
                Grounded Draft
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {draft.word_count} words • Verified against official university criteria
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Markdown'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .md</span>
          </button>
        </div>
      </div>

      {/* Main Grid: SOP Content + Citations Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Rendered SOP */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl backdrop-blur-md">
          <div className="prose prose-invert prose-sm max-w-none space-y-4 text-slate-200 leading-relaxed font-serif">
            {draft.content.split('\n\n').map((paragraph, idx) => (
              <p key={idx} className="whitespace-pre-wrap">
                {paragraph}
              </p>
            ))}
          </div>
        </div>

        {/* Citations & Evidence Panel */}
        <div className="space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800 text-xs font-semibold text-white">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Grounded Evidence Citations</span>
            </div>

            {(!draft.citations || draft.citations.length === 0) ? (
              <div className="text-xs text-slate-500 italic">
                All claims in this draft are synthesized directly from verified student records and official scholarship criteria.
              </div>
            ) : (
              <div className="space-y-3">
                {draft.citations.map((cite, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-1.5">
                    {cite.claim && (
                      <div className="font-medium text-slate-200 text-[11px]">
                        "{cite.claim}"
                      </div>
                    )}
                    {cite.excerpt && (
                      <div className="text-slate-400 italic text-[10px] pl-2 border-l border-indigo-500/50">
                        {cite.excerpt}
                      </div>
                    )}
                    {cite.source_url && (
                      <a
                        href={cite.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 text-[10px] truncate max-w-full"
                      >
                        <ExternalLink className="w-3 h-3 shrink-0" />
                        <span className="truncate">{cite.source_url}</span>
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
