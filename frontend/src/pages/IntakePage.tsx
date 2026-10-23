// IntakePage for student profile registration, document upload, and quick demo loading

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  User,
  GraduationCap,
  Globe,
  Code2,
  ArrowRight,
  FileText,
  AlertCircle,
  X,
} from 'lucide-react';
import { useCreateProfile, useStartResearchJob, useUploadDocument } from '../api/hooks';
import type { DegreeLevel, StudentProfile } from '../types/api';

export const IntakePage: React.FC = () => {
  const navigate = useNavigate();
  const createProfile = useCreateProfile();
  const startJob = useStartResearchJob();

  // Form states
  const [fullName, setFullName] = useState('Rahul Sharma');
  const [nationality, setNationality] = useState('India');
  const [degreeHeld, setDegreeHeld] = useState<DegreeLevel>('bachelor');
  const [degreeTarget, setDegreeTarget] = useState<DegreeLevel>('master');
  const [fieldOfStudy, setFieldOfStudy] = useState('Computer Science');
  const [institution, setInstitution] = useState('Delhi Technological University');
  const [graduationYear, setGraduationYear] = useState('2025');
  const [gradeValue, setGradeValue] = useState('8.2');
  const [gradeScale, setGradeScale] = useState('10.0');
  const [targetCountries, setTargetCountries] = useState('Germany, Canada, Singapore');
  const [interests, setInterests] = useState('Artificial Intelligence, Distributed Systems, Machine Learning');
  const [githubUrl, setGithubUrl] = useState('https://github.com/torvalds');
  const [budgetNote, setBudgetNote] = useState('Requires partial or full scholarship to fund graduate studies');
  const [needsFunding, setNeedsFunding] = useState(true);

  // Document upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Quick Demo Pre-fill helpers
  const loadRahulDemo = () => {
    setFullName('Rahul Sharma');
    setNationality('India');
    setDegreeHeld('bachelor');
    setDegreeTarget('master');
    setFieldOfStudy('Computer Science');
    setInstitution('Delhi Technological University');
    setGraduationYear('2025');
    setGradeValue('8.2');
    setGradeScale('10.0');
    setTargetCountries('Germany, Canada, Singapore');
    setInterests('Artificial Intelligence, Distributed Systems, Machine Learning');
    setGithubUrl('https://github.com/torvalds');
    setBudgetNote('Requires partial or full scholarship to fund graduate studies');
    setNeedsFunding(true);
  };

  const loadAnanyaDemo = () => {
    setFullName('Ananya Iyer');
    setNationality('India');
    setDegreeHeld('bachelor');
    setDegreeTarget('master');
    setFieldOfStudy('Biotechnology');
    setInstitution('Anna University');
    setGraduationYear('2024');
    setGradeValue('8.9');
    setGradeScale('10.0');
    setTargetCountries('United Kingdom, Germany, Sweden');
    setInterests('Computational Biology, Genomics, Bioinformatics');
    setGithubUrl('https://github.com/tiangolo');
    setBudgetNote('Seeking merit-based scholarship or fellowship');
    setNeedsFunding(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMessage(null);

    try {
      const countriesList = targetCountries
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      const interestsList = interests
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      const profilePayload: Partial<StudentProfile> = {
        full_name: fullName.trim(),
        nationality: nationality.trim(),
        degree_level_held: degreeHeld,
        degree_level_target: degreeTarget,
        field_of_study: fieldOfStudy.trim(),
        institution: institution.trim(),
        graduation_year: graduationYear ? parseInt(graduationYear, 10) : undefined,
        grade: {
          value: parseFloat(gradeValue) || 0.0,
          scale: parseFloat(gradeScale) || 10.0,
        },
        language_tests: [],
        target_countries: countriesList,
        interests: interestsList,
        budget_note: budgetNote.trim(),
        needs_funding: needsFunding,
        github_url: githubUrl.trim() || undefined,
      };

      const profileRes = await createProfile.mutateAsync(profilePayload);
      const profileId = profileRes.id;

      if (selectedFile) {
        try {
          const uploadMutation = useUploadDocument(profileId);
          await uploadMutation.mutateAsync({ kind: 'resume', file: selectedFile });
        } catch {
          // Document upload failure does not block job execution
        }
      }

      const job = await startJob.mutateAsync({
        profileId,
        countries: countriesList,
        maxCandidates: 12,
      });

      localStorage.setItem('scholarpilot_last_job_id', job.id);
      navigate(`/jobs/${job.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to initialize research job. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-xl sm:text-2xl font-semibold text-zinc-100 tracking-tight">
          Scholarship Research Intake
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
          Supply your academic profile. Our cooperative agent team searches official university portals,
          verifies criteria against primary sources, and ranks top opportunities.
        </p>

        {/* Demo profile triggers */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <span className="text-xs text-zinc-500 font-medium">Quick Profiles:</span>
          <button
            type="button"
            onClick={loadRahulDemo}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 text-xs transition-colors"
          >
            <User className="w-3.5 h-3.5 text-zinc-400" />
            Rahul (CS, 8.2 CGPA)
          </button>
          <button
            type="button"
            onClick={loadAnanyaDemo}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 text-xs transition-colors"
          >
            <GraduationCap className="w-3.5 h-3.5 text-zinc-400" />
            Ananya (Biotech, 8.9 CGPA)
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Intake Form */}
      <form onSubmit={handleSubmit} className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5 sm:p-6 space-y-6">
        {/* Section 1: Academic Background */}
        <div className="space-y-3.5">
          <div className="flex items-center gap-2 pb-2 border-b border-zinc-800 text-xs font-semibold text-zinc-200">
            <User className="w-3.5 h-3.5 text-zinc-400" />
            <span>1. Academic Background</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Nationality</label>
              <input
                type="text"
                required
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Degree Held</label>
              <select
                value={degreeHeld}
                onChange={(e) => setDegreeHeld(e.target.value as DegreeLevel)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              >
                <option value="bachelor">Bachelor</option>
                <option value="master">Master</option>
                <option value="phd">PhD</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Target Degree</label>
              <select
                value={degreeTarget}
                onChange={(e) => setDegreeTarget(e.target.value as DegreeLevel)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              >
                <option value="master">Master (Graduate Studies)</option>
                <option value="phd">PhD (Doctorate)</option>
                <option value="bachelor">Bachelor</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Field of Study</label>
              <input
                type="text"
                required
                value={fieldOfStudy}
                onChange={(e) => setFieldOfStudy(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Undergraduate Institution</label>
              <input
                type="text"
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">CGPA / Score</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={gradeValue}
                  onChange={(e) => setGradeValue(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">Scale (e.g. 10.0)</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={gradeScale}
                  onChange={(e) => setGradeScale(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Graduation Year</label>
              <input
                type="number"
                value={graduationYear}
                onChange={(e) => setGraduationYear(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Preferences & Footprint */}
        <div className="space-y-3.5">
          <div className="flex items-center gap-2 pb-2 border-b border-zinc-800 text-xs font-semibold text-zinc-200">
            <Globe className="w-3.5 h-3.5 text-zinc-400" />
            <span>2. Preferences & Online Footprint</span>
          </div>

          <div className="space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Target Countries (comma separated)
              </label>
              <input
                type="text"
                required
                value={targetCountries}
                onChange={(e) => setTargetCountries(e.target.value)}
                placeholder="e.g. Germany, Canada, Singapore"
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Research Interests & Technical Skills
              </label>
              <input
                type="text"
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g. Artificial Intelligence, Distributed Systems"
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1 flex items-center gap-1.5">
                  <Code2 className="w-3.5 h-3.5 text-zinc-400" />
                  GitHub URL (for project enrichment)
                </label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username"
                  className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">Budget / Funding Need</label>
                <input
                  type="text"
                  value={budgetNote}
                  onChange={(e) => setBudgetNote(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs focus:outline-none focus:border-zinc-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Document Attachment */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2 pb-2 border-b border-zinc-800 text-xs font-semibold text-zinc-200">
            <Upload className="w-3.5 h-3.5 text-zinc-400" />
            <span>3. Upload Resume or Transcript (Optional)</span>
          </div>

          <div className="border border-dashed border-zinc-800 hover:border-zinc-700 rounded-lg p-4 text-center cursor-pointer transition-colors bg-zinc-950/60">
            <input
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="hidden"
              id="file-upload"
            />
            {selectedFile ? (
              <div className="flex items-center justify-between px-2 text-xs">
                <div className="flex items-center gap-2 text-zinc-200">
                  <FileText className="w-4 h-4 text-zinc-400" />
                  <span className="font-medium">{selectedFile.name}</span>
                  <span className="text-zinc-500">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="p-1 hover:bg-zinc-800 text-zinc-400 rounded"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <label htmlFor="file-upload" className="cursor-pointer block">
                <FileText className="w-5 h-5 text-zinc-500 mx-auto mb-1" />
                <span className="text-xs text-zinc-300 font-medium block">
                  Click to attach a PDF or text document
                </span>
                <span className="text-[11px] text-zinc-500">Parsed with SSRF protection & BM25 retrieval (Max 5MB)</span>
              </label>
            )}
          </div>
        </div>

        {/* Submit */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 px-4 rounded-lg bg-zinc-100 hover:bg-white text-zinc-900 font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm disabled:opacity-50"
          >
            {submitting ? (
              <span>Deploying Agents...</span>
            ) : (
              <>
                <span>Start Research Swarm</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
