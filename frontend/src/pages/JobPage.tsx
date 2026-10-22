// JobPage displaying live 5-agent swarm progress and Evidence-Backed Eligibility Report

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  RefreshCw,
  StopCircle,
  AlertTriangle,
  Award,
  ListFilter,
  UserCheck,
  ExternalLink,
} from 'lucide-react';
import {
  useJob,
  useJobEvents,
  useJobResults,
  useCancelJob,
  useRetryJob,
  useGenerateDraft,
} from '../api/hooks';
import { AgentTimeline } from '../components/AgentTimeline';
import { OpportunityCard } from '../components/OpportunityCard';
import { EvidenceDrawer } from '../components/EvidenceDrawer';
import { StatusPill } from '../components/StatusPill';
import type { CriterionAssessment, JobStatus } from '../types/api';

export const JobPage: React.FC = () => {
  const { id: jobId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Queries and mutations
  const { data: job, isLoading: jobLoading, refetch: refetchJob } = useJob(jobId);
  const isTerminal = job?.status === 'completed' || job?.status === 'completed_with_warnings' || job?.status === 'failed' || job?.status === 'cancelled';
  const { data: eventsData } = useJobEvents(jobId, !isTerminal);
  const { data: results, isLoading: resultsLoading } = useJobResults(jobId, isTerminal || Boolean(job?.status));

  const cancelJob = useCancelJob();
  const retryJob = useRetryJob();
  const generateDraft = useGenerateDraft();

  // Local UI state
  const [activeTab, setActiveTab] = useState<'top' | 'all' | 'profile' | 'warnings'>('top');
  const [selectedAssessment, setSelectedAssessment] = useState<CriterionAssessment | null>(null);
  const [draftingOppId, setDraftingOppId] = useState<string | null>(null);

  const events = eventsData?.events || [];
  const currentStatus: JobStatus = job?.status || 'queued';

  // Actions
  const handleCancel = async () => {
    if (!jobId) return;
    await cancelJob.mutateAsync(jobId);
    refetchJob();
  };

  const handleRetry = async () => {
    if (!jobId) return;
    await retryJob.mutateAsync(jobId);
    refetchJob();
  };

  const handleDraftSop = async (oppId: string) => {
    if (!jobId) return;
    try {
      setDraftingOppId(oppId);
      const draft = await generateDraft.mutateAsync({
        jobId,
        opportunityId: oppId,
        tone: 'academic',
      });
      navigate(`/jobs/${jobId}/draft/${draft.id}`);
    } catch (err: any) {
      alert(`Could not generate SOP draft: ${err.message || 'Provider timeout'}`);
    } finally {
      setDraftingOppId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-slate-400">Job: {jobId}</span>
            <StatusPill status={currentStatus} />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Evidence-Backed Eligibility Report
          </h1>
          <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
            <span>Started: {job?.started_at ? new Date(job.started_at).toLocaleTimeString() : 'Queued'}</span>
            {job?.finished_at && (
              <span>• Finished: {new Date(job.finished_at).toLocaleTimeString()}</span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {(currentStatus === 'queued' || currentStatus === 'running') && (
            <button
              onClick={handleCancel}
              disabled={cancelJob.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors"
            >
              <StopCircle className="w-4 h-4 text-rose-400" />
              Cancel Job
            </button>
          )}

          {(currentStatus === 'failed' || currentStatus === 'cancelled') && (
            <button
              onClick={handleRetry}
              disabled={retryJob.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              Resume from Checkpoint
            </button>
          )}

          <button
            onClick={() => refetchJob()}
            className="p-2 rounded-xl bg-slate-800/60 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh Status"
          >
            <RefreshCw className={`w-4 h-4 ${jobLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Five-Lane Agent Swarm Timeline */}
      <AgentTimeline events={events} jobStatus={currentStatus} />

      {/* Results View Tabs */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('top')}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'top'
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Award className="w-4 h-4 text-indigo-400" />
            Top 5 Ranked Scholarships ({results?.top?.length || 0})
          </button>

          <button
            onClick={() => setActiveTab('all')}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'all'
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ListFilter className="w-4 h-4 text-sky-400" />
            All Candidates Discovered ({results?.all?.length || 0})
          </button>

          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'profile'
                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserCheck className="w-4 h-4 text-teal-400" />
            Profile & GitHub Enrichment
          </button>

          {results?.warnings && results.warnings.length > 0 && (
            <button
              onClick={() => setActiveTab('warnings')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'warnings'
                  ? 'bg-amber-600/20 text-amber-300 border border-amber-500/30'
                  : 'text-amber-400/80 hover:text-amber-300'
              }`}
            >
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Warnings ({results.warnings.length})
            </button>
          )}
        </div>

        {/* Tab 1: Top 5 Scholarships */}
        {activeTab === 'top' && (
          <div className="space-y-4">
            {resultsLoading && (
              <div className="p-12 text-center text-slate-400 space-y-3">
                <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
                <p className="text-sm">Agents evaluating criteria and computing 6-factor ranking...</p>
              </div>
            )}

            {!resultsLoading && (!results?.top || results.top.length === 0) && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 space-y-2">
                <p className="text-sm font-medium text-slate-300">
                  {currentStatus === 'running'
                    ? 'Swarm agents are currently discovering opportunities and verifying official sources...'
                    : 'No opportunities qualified for the Top 5 list based on current filters.'}
                </p>
                <p className="text-xs text-slate-500">
                  Review the "All Candidates" tab to see all assessed entries.
                </p>
              </div>
            )}

            {results?.top?.map((item) => (
              <OpportunityCard
                key={item.opportunity.id}
                item={item}
                onSelectEvidence={(a) => setSelectedAssessment(a)}
                onDraftSop={(oppId) => handleDraftSop(oppId)}
                isDrafting={draftingOppId === item.opportunity.id}
              />
            ))}
          </div>
        )}

        {/* Tab 2: All Discovered Candidates */}
        {activeTab === 'all' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-medium">
                  <th className="py-2.5 px-3">Opportunity Name</th>
                  <th className="py-2.5 px-3">Institution</th>
                  <th className="py-2.5 px-3">Country</th>
                  <th className="py-2.5 px-3">Funding</th>
                  <th className="py-2.5 px-3">Deadline</th>
                  <th className="py-2.5 px-3">Verification</th>
                  <th className="py-2.5 px-3">Overall Eligibility</th>
                  <th className="py-2.5 px-3 text-right">Official Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {results?.all?.map((cand) => (
                  <tr key={cand.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-semibold text-white max-w-[200px] truncate" title={cand.name}>
                      {cand.name}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">{cand.institution || '—'}</td>
                    <td className="py-2.5 px-3">{cand.country || '—'}</td>
                    <td className="py-2.5 px-3 uppercase text-slate-400">{cand.funding_type?.replace('_', ' ')}</td>
                    <td className="py-2.5 px-3">{cand.deadline || 'Ongoing'}</td>
                    <td className="py-2.5 px-3">
                      <StatusPill status={cand.verification_status} size="sm" />
                    </td>
                    <td className="py-2.5 px-3">
                      <StatusPill status={cand.overall} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      {cand.official_url ? (
                        <a
                          href={cand.official_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 text-[11px]"
                        >
                          <ExternalLink className="w-3 h-3" />
                          View
                        </a>
                      ) : (
                        <span className="text-slate-600 text-[11px]">Unreachable</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 3: Profile & GitHub Enrichment */}
        {activeTab === 'profile' && results?.profile && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div>
              <h3 className="text-base font-bold text-white mb-1">
                {results.profile.full_name} ({results.profile.nationality})
              </h3>
              <p className="text-xs text-slate-400">
                {results.profile.degree_level_target?.toUpperCase()} in {results.profile.field_of_study} • CGPA {results.profile.grade?.value}/{results.profile.grade?.scale}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">Academic Preferences</span>
                <div className="text-slate-400">Target Countries: {results.profile.target_countries?.join(', ')}</div>
                <div className="text-slate-400">Interests: {results.profile.interests?.join(', ')}</div>
                <div className="text-slate-400">Funding Need: {results.profile.needs_funding ? 'Yes (requires funding)' : 'No'}</div>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">GitHub Profile Enrichment</span>
                {results.profile.github_url ? (
                  <>
                    <a
                      href={results.profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono text-[11px]"
                    >
                      <ExternalLink className="w-3 h-3" />
                      {results.profile.github_url}
                    </a>
                    {results.profile.projects && results.profile.projects.length > 0 && (
                      <div className="space-y-1.5 mt-2">
                        {results.profile.projects.map((p, idx) => (
                          <div key={idx} className="p-2 rounded bg-slate-900/80 border border-slate-800 text-[11px]">
                            <div className="font-semibold text-white">{p.name}</div>
                            <div className="text-slate-400">{p.summary}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-slate-500 italic">No public GitHub profile supplied.</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Agent Warnings & Audit */}
        {activeTab === 'warnings' && results?.warnings && (
          <div className="space-y-3">
            {results.warnings.map((w, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-amber-300 uppercase tracking-wider text-[10px]">[{w.agent}] </span>
                  <span>{w.message}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Slide-over Evidence Drawer */}
      <EvidenceDrawer
        assessment={selectedAssessment}
        onClose={() => setSelectedAssessment(null)}
      />
    </div>
  );
};
