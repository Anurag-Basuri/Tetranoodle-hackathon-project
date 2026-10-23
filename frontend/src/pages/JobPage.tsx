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
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Header bar */}
      <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono text-zinc-500">ID: {jobId}</span>
            <StatusPill status={currentStatus} />
          </div>
          <h1 className="text-lg sm:text-xl font-semibold text-zinc-100 tracking-tight">
            Evidence-Backed Eligibility Report
          </h1>
          <div className="flex items-center gap-2 text-xs text-zinc-400 mt-1">
            <span>Started: {job?.started_at ? new Date(job.started_at).toLocaleTimeString() : 'Queued'}</span>
            {job?.finished_at && (
              <>
                <span>•</span>
                <span>Finished: {new Date(job.finished_at).toLocaleTimeString()}</span>
              </>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {(currentStatus === 'queued' || currentStatus === 'running') && (
            <button
              onClick={handleCancel}
              disabled={cancelJob.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium border border-zinc-700 transition-colors"
            >
              <StopCircle className="w-3.5 h-3.5 text-rose-400" />
              Cancel Job
            </button>
          )}

          {(currentStatus === 'failed' || currentStatus === 'cancelled') && (
            <button
              onClick={handleRetry}
              disabled={retryJob.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold shadow-sm transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Resume Checkpoint
            </button>
          )}

          <button
            onClick={() => refetchJob()}
            className="p-1.5 rounded-lg bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 border border-zinc-700 transition-colors"
            title="Refresh Status"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${jobLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Multi-Agent Pipeline Visualizer */}
      <AgentTimeline events={events} jobStatus={currentStatus} />

      {/* Tabs and Results Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-1 border-b border-zinc-800 pb-2">
          <button
            onClick={() => setActiveTab('top')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'top'
                ? 'bg-zinc-800 text-zinc-100'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Award className="w-3.5 h-3.5 text-zinc-400" />
            Top 5 Recommendations ({results?.top?.length || 0})
          </button>

          <button
            onClick={() => setActiveTab('all')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'all'
                ? 'bg-zinc-800 text-zinc-100'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <ListFilter className="w-3.5 h-3.5 text-zinc-400" />
            All Candidates Discovered ({results?.all?.length || 0})
          </button>

          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'profile'
                ? 'bg-zinc-800 text-zinc-100'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <UserCheck className="w-3.5 h-3.5 text-zinc-400" />
            Profile & Footprint
          </button>

          {results?.warnings && results.warnings.length > 0 && (
            <button
              onClick={() => setActiveTab('warnings')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === 'warnings'
                  ? 'bg-amber-950/40 text-amber-300 border border-amber-800/50'
                  : 'text-amber-400/80 hover:text-amber-300'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              Warnings ({results.warnings.length})
            </button>
          )}
        </div>

        {/* Tab 1: Top 5 Recommendations */}
        {activeTab === 'top' && (
          <div className="space-y-4">
            {resultsLoading && (
              <div className="p-8 text-center text-zinc-400 space-y-2">
                <RefreshCw className="w-5 h-5 animate-spin text-zinc-400 mx-auto" />
                <p className="text-xs">Evaluating criteria and computing rankings...</p>
              </div>
            )}

            {!resultsLoading && (!results?.top || results.top.length === 0) && (
              <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-8 text-center text-zinc-400 space-y-1.5">
                <p className="text-xs font-medium text-zinc-300">
                  {currentStatus === 'running'
                    ? 'Swarm agents are discovering opportunities and verifying official sources...'
                    : 'No opportunities qualified for the Top 5 list based on current filters.'}
                </p>
                <p className="text-[11px] text-zinc-500">
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
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-4 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-400 font-medium">
                  <th className="py-2 px-3">Opportunity</th>
                  <th className="py-2 px-3">Institution</th>
                  <th className="py-2 px-3">Country</th>
                  <th className="py-2 px-3">Funding</th>
                  <th className="py-2 px-3">Deadline</th>
                  <th className="py-2 px-3">Verification</th>
                  <th className="py-2 px-3">Eligibility</th>
                  <th className="py-2 px-3 text-right">Official Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
                {results?.all?.map((cand) => (
                  <tr key={cand.id} className="hover:bg-zinc-800/30">
                    <td className="py-2.5 px-3 font-medium text-zinc-200 max-w-[200px] truncate" title={cand.name}>
                      {cand.name}
                    </td>
                    <td className="py-2.5 px-3 text-zinc-400">{cand.institution || '—'}</td>
                    <td className="py-2.5 px-3">{cand.country || '—'}</td>
                    <td className="py-2.5 px-3 capitalize text-zinc-400">{cand.funding_type?.replace('_', ' ')}</td>
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
                          className="inline-flex items-center gap-1 text-zinc-400 hover:text-zinc-200 text-[11px] underline underline-offset-2"
                        >
                          Official
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-zinc-600 text-[11px]">Unreachable</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 3: Profile & Footprint */}
        {activeTab === 'profile' && results?.profile && (
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5 space-y-5">
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">
                {results.profile.full_name} ({results.profile.nationality})
              </h3>
              <p className="text-xs text-zinc-400 mt-0.5">
                {results.profile.degree_level_target?.toUpperCase()} in {results.profile.field_of_study} • CGPA {results.profile.grade?.value}/{results.profile.grade?.scale}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
              <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 space-y-2">
                <span className="font-medium text-zinc-300 uppercase tracking-wider text-[11px]">Academic Preferences</span>
                <div className="text-zinc-400">Target Destinations: {results.profile.target_countries?.join(', ')}</div>
                <div className="text-zinc-400">Interests: {results.profile.interests?.join(', ')}</div>
                <div className="text-zinc-400">Funding Requirement: {results.profile.needs_funding ? 'Yes (requires funding)' : 'No'}</div>
              </div>

              <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 space-y-2">
                <span className="font-medium text-zinc-300 uppercase tracking-wider text-[11px]">GitHub Enriched Projects</span>
                {results.profile.github_url ? (
                  <>
                    <a
                      href={results.profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 flex items-center gap-1 font-mono text-[11px]"
                    >
                      {results.profile.github_url}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    {results.profile.projects && results.profile.projects.length > 0 && (
                      <div className="space-y-1.5 mt-2">
                        {results.profile.projects.map((p, idx) => (
                          <div key={idx} className="p-2 rounded bg-zinc-900 border border-zinc-800 text-[11px]">
                            <div className="font-medium text-zinc-200">{p.name}</div>
                            <div className="text-zinc-400">{p.summary}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-zinc-500 italic">No public GitHub profile supplied.</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Agent Warnings & Audit */}
        {activeTab === 'warnings' && results?.warnings && (
          <div className="space-y-2.5">
            {results.warnings.map((w, idx) => (
              <div key={idx} className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-800/40 text-amber-200 text-xs flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-medium text-amber-300 uppercase tracking-wider text-[10px]">[{w.agent}] </span>
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
