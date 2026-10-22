// IntakePage for student profile registration, document upload, and quick demo loading

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Upload,
  User,
  GraduationCap,
  Globe,
  Code2,
  ArrowRight,
  FileText,
  AlertCircle,
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

  // Quick Demo Profiles pre-fill
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
      // 1. Build profile payload
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

      // 2. Register profile
      const profileRes = await createProfile.mutateAsync(profilePayload);
      const profileId = profileRes.id;

      // 3. Optional: Upload resume document if attached
      if (selectedFile) {
        try {
          const uploadMutation = useUploadDocument(profileId);
          await uploadMutation.mutateAsync({ kind: 'resume', file: selectedFile });
        } catch {
          // Document upload failure does not block research job start
        }
      }

      // 4. Start Autonomous Multi-Agent Swarm Job
      const job = await startJob.mutateAsync({
        profileId,
        countries: countriesList,
        maxCandidates: 12,
      });

      localStorage.setItem('scholarpilot_last_job_id', job.id);
      navigate(`/jobs/${job.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to initialize research swarm. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Hero Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          Autonomous 5-Agent Scholarship Swarm
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Evidence-Backed Scholarship Research
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
          Supply your academic profile. Our cooperative agent team searches official university portals,
          verifies eligibility criteria against primary sources, and ranks your Top 5 matches.
        </p>

        {/* Quick Demo Pre-fills */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={loadRahulDemo}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold shadow-sm transition-all"
          >
            <User className="w-3.5 h-3.5 text-indigo-400" />
            Load Demo Profile (Rahul: CS, 8.2 CGPA)
          </button>
          <button
            type="button"
            onClick={loadAnanyaDemo}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold shadow-sm transition-all"
          >
            <GraduationCap className="w-3.5 h-3.5 text-teal-400" />
            Load Second Profile (Ananya: Biotech, 8.9 CGPA)
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-md shadow-2xl space-y-6">
        {/* Section 1: Personal & Academic Basics */}
        <div>
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <User className="w-4 h-4 text-indigo-400" />
            1. Student Academic Profile
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Nationality</label>
              <input
                type="text"
                required
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Degree Held</label>
              <select
                value={degreeHeld}
                onChange={(e) => setDegreeHeld(e.target.value as DegreeLevel)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="bachelor">Bachelor</option>
                <option value="master">Master</option>
                <option value="phd">PhD</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target Degree</label>
              <select
                value={degreeTarget}
                onChange={(e) => setDegreeTarget(e.target.value as DegreeLevel)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              >
                <option value="master">Master (Graduate Studies)</option>
                <option value="phd">PhD (Doctorate)</option>
                <option value="bachelor">Bachelor</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Field of Study</label>
              <input
                type="text"
                required
                value={fieldOfStudy}
                onChange={(e) => setFieldOfStudy(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Undergraduate Institution</label>
              <input
                type="text"
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">CGPA / Grade</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={gradeValue}
                  onChange={(e) => setGradeValue(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Scale (e.g. 10 or 4)</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={gradeScale}
                  onChange={(e) => setGradeScale(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Graduation Year</label>
              <input
                type="number"
                value={graduationYear}
                onChange={(e) => setGraduationYear(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Preferences & Enrichment */}
        <div className="pt-4 border-t border-slate-800">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Globe className="w-4 h-4 text-sky-400" />
            2. Search Preferences & Online Footprint
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Target Countries (comma separated)
              </label>
              <input
                type="text"
                required
                value={targetCountries}
                onChange={(e) => setTargetCountries(e.target.value)}
                placeholder="e.g. Germany, Canada, Singapore"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Research Interests & Technical Skills
              </label>
              <input
                type="text"
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g. Artificial Intelligence, Distributed Systems"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1.5">
                  <Code2 className="w-3.5 h-3.5 text-slate-400" />
                  GitHub Profile URL (Agent 1 Enriches Projects)
                </label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username"
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Budget / Funding Need</label>
                <input
                  type="text"
                  value={budgetNote}
                  onChange={(e) => setBudgetNote(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Document Attachment */}
        <div className="pt-4 border-t border-slate-800">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
            <Upload className="w-4 h-4 text-teal-400" />
            3. Upload Resume / Transcript (Optional)
          </h2>
          <p className="text-xs text-slate-400 mb-3">
            Parsed with SSRF protection and chunked via BM25 retrieval for evidence verification.
          </p>

          <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-2xl p-4 text-center cursor-pointer transition-colors bg-slate-950/40">
            <input
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <FileText className="w-6 h-6 text-indigo-400 mb-1" />
              <span className="text-xs text-slate-300 font-medium">
                {selectedFile ? selectedFile.name : 'Click to select PDF or text document'}
              </span>
              <span className="text-[11px] text-slate-500 mt-0.5">Maximum file size: 5MB</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-sky-500 hover:from-indigo-500 hover:to-sky-400 text-white text-sm font-bold shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {submitting ? (
              <span>Deploying Multi-Agent Swarm...</span>
            ) : (
              <>
                <span>Launch Autonomous Research Swarm</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
