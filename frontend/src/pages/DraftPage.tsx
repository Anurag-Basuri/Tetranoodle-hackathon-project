// DraftPage for reviewing, copying, and exporting grounded Statement of Purpose drafts

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Copy,
  Check,
  Download,
  ArrowLeft,
  ExternalLink,
  ShieldCheck,
  Loader2,
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
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-zinc-400 space-y-2">
        <Loader2 className="w-5 h-5 animate-spin mx-auto text-zinc-400" />
        <p className="text-xs">Loading Statement of Purpose draft...</p>
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-zinc-400 space-y-3">
        <p className="text-xs">Draft not found or expired.</p>
        <button
          onClick={() => navigate(`/jobs/${jobId}`)}
          className="px-3.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium"
        >
          Back to Report
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Top action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-zinc-900/40 border border-zinc-800 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(`/jobs/${jobId}`)}
            className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 transition-colors"
            title="Back to Research Report"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-zinc-100">Statement of Purpose Draft</h1>
              <span className="px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700 text-[10px] font-mono">
                verified draft
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              {draft.word_count} words • Formulated from official criteria and student records
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium border border-zinc-700 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-zinc-400" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .md</span>
          </button>
        </div>
      </div>

      {/* Main Grid: SOP Content + Citations Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Rendered SOP */}
        <div className="lg:col-span-2 bg-zinc-900/40 border border-zinc-800 rounded-xl p-6 sm:p-7">
          <div className="space-y-4 text-zinc-200 leading-relaxed font-serif text-sm">
            {draft.content.split('\n\n').map((paragraph, idx) => (
              <p key={idx} className="whitespace-pre-wrap">
                {paragraph}
              </p>
            ))}
          </div>
        </div>

        {/* Citations & Evidence Panel */}
        <div className="space-y-3">
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2 pb-2.5 border-b border-zinc-800 text-xs font-semibold text-zinc-200">
              <ShieldCheck className="w-4 h-4 text-zinc-400" />
              <span>Grounded Evidence Citations</span>
            </div>

            {(!draft.citations || draft.citations.length === 0) ? (
              <div className="text-xs text-zinc-500 italic">
                Claims in this statement are grounded directly in student records and verified scholarship requirements.
              </div>
            ) : (
              <div className="space-y-2.5">
                {draft.citations.map((cite, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-xs space-y-1">
                    {cite.claim && (
                      <div className="font-medium text-zinc-300 text-[11px]">
                        "{cite.claim}"
                      </div>
                    )}
                    {cite.excerpt && (
                      <div className="text-zinc-400 italic text-[10px] pl-2 border-l border-zinc-700">
                        {cite.excerpt}
                      </div>
                    )}
                    {cite.source_url && (
                      <a
                        href={cite.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 text-[10px] truncate max-w-full underline underline-offset-2"
                      >
                        Source
                        <ExternalLink className="w-2.5 h-2.5 shrink-0" />
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
