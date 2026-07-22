"use client";

import React, { useState, useEffect } from "react";

interface HealthStatus {
  status: string;
  database: string;
  project: string;
  version: string;
  environment: string;
}

interface ParsedResume {
  contact_info: {
    name: string | null;
    email: string | null;
    phone: string | null;
    linkedin: string | null;
    github: string | null;
  };
  summary: string;
  skills: string[];
}

interface ResumeResponseData {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  raw_text: string | null;
  parsed_data: ParsedResume | null;
  status: string;
}

interface JobDescriptionResponseData {
  id: string;
  title: string;
  company: string | null;
  raw_text: string;
  required_skills: Record<string, any> | null;
  preferred_skills: Record<string, any> | null;
  parsed_requirements: Record<string, any> | null;
}

interface MatchResultData {
  id: string;
  resume_id: string;
  job_description_id: string;
  overall_score: number;
  skills_score: number | null;
  experience_score: number | null;
  education_score: number | null;
  matched_skills: { skills: string[] } | null;
  missing_skills: { skills: string[] } | null;
  breakdown: {
    skills_match_weight: number;
    semantic_weight: number;
    experience_weight: number;
    ai_feedback?: string;
  } | null;
}

const renderMarkdown = (text: string) => {
  if (!text) return null;
  const lines = text.split("\n");
  return (
    <div className="space-y-3">
      {lines.map((line, idx) => {
        let cleanLine = line.trim();
        if (!cleanLine) return null;

        // Check for bullet items
        const isBullet = cleanLine.startsWith("* ") || cleanLine.startsWith("• ");
        if (isBullet) {
          cleanLine = cleanLine.slice(2);
        }

        // Format bold markers **text**
        const parts = cleanLine.split(/\*\*(.*?)\*\*/g);
        const elements = parts.map((part, i) => {
          if (i % 2 === 1) {
            return (
              <strong key={i} className="text-white font-bold font-sans">
                {part}
              </strong>
            );
          }
          return part;
        });

        if (isBullet) {
          return (
            <div key={idx} className="flex gap-2 text-zinc-300 pl-2">
              <span className="text-indigo-400 select-none">•</span>
              <p className="leading-relaxed flex-1">{elements}</p>
            </div>
          );
        }

        return (
          <p key={idx} className="text-zinc-300 leading-relaxed font-medium">
            {elements}
          </p>
        );
      })}
    </div>
  );
};

export default function Home() {
  const BACKEND_URL = "http://localhost:8000/api/v1";

  // State
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Resume Ingestion State
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);
  const [resumeResult, setResumeResult] = useState<ResumeResponseData | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);

  // Job Description State
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdText, setJdText] = useState("");
  const [jdIngesting, setJdIngesting] = useState(false);
  const [jdResult, setJdResult] = useState<JobDescriptionResponseData | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);

  // Matching Configuration and State
  const [skillsWeight, setSkillsWeight] = useState(0.5);
  const [semanticWeight, setSemanticWeight] = useState(0.3);
  const [experienceWeight, setExperienceWeight] = useState(0.2);
  const [matchEvaluating, setMatchEvaluating] = useState(false);
  const [matchResult, setMatchResult] = useState<MatchResultData | null>(null);
  const [matchError, setMatchError] = useState<string | null>(null);

  // Load API Health on mount
  const checkHealth = async () => {
    setHealthLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      } else {
        setHealth(null);
      }
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  // Upload Resume handler
  const handleResumeUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeFile) return;

    setResumeUploading(true);
    setResumeError(null);
    setResumeResult(null);

    const formData = new FormData();
    formData.append("file", resumeFile);

    try {
      const res = await fetch(`${BACKEND_URL}/resumes/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error?.message || "Failed to upload and parse resume.");
      }

      const data = await res.json();
      setResumeResult(data);
    } catch (err: any) {
      setResumeError(err.message || "An unexpected error occurred during resume ingestion.");
    } finally {
      setResumeUploading(false);
    }
  };

  // Ingest Job Description handler
  const handleJdIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdTitle.trim() || !jdText.trim()) return;

    setJdIngesting(true);
    setJdError(null);
    setJdResult(null);

    try {
      const res = await fetch(`${BACKEND_URL}/jd/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: jdTitle,
          company: jdCompany || null,
          raw_text: jdText,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error?.message || "Failed to create job description.");
      }

      const data = await res.json();
      setJdResult(data);
    } catch (err: any) {
      setJdError(err.message || "An unexpected error occurred during Job Description ingestion.");
    } finally {
      setJdIngesting(false);
    }
  };

  // Run ATS Match Evaluation
  const handleEvaluateMatch = async () => {
    if (!resumeResult?.id || !jdResult?.id) return;

    setMatchEvaluating(true);
    setMatchError(null);
    setMatchResult(null);

    // Normalize weights to sum to 1.0 (or warn if they don't, but let's pass them)
    try {
      const res = await fetch(`${BACKEND_URL}/matching/evaluate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_id: resumeResult.id,
          job_description_id: jdResult.id,
          weights: {
            skills_weight: skillsWeight,
            semantic_weight: semanticWeight,
            experience_weight: experienceWeight,
            education_weight: 0.0, // Unused in default math
          },
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error?.message || "Match evaluation failed.");
      }

      const data = await res.json();
      setMatchResult(data);
    } catch (err: any) {
      setMatchError(err.message || "An unexpected error occurred during match evaluation.");
    } finally {
      setMatchEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500 selection:text-white pb-20">
      {/* Navbar Banner */}
      <header className="border-b border-zinc-800 bg-zinc-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-indigo-500/20">
              IQ
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-200 via-purple-200 to-white bg-clip-text text-transparent">
                ResumeIQ AI
              </h1>
              <p className="text-[10px] text-zinc-400 font-mono">
                Developer Integration & Verification Suite
              </p>
            </div>
          </div>

          {/* API Health Pill */}
          <div className="flex items-center gap-4">
            <button
              onClick={checkHealth}
              disabled={healthLoading}
              className="text-xs text-zinc-400 hover:text-white transition-colors bg-zinc-800 hover:bg-zinc-700 px-3 py-1.5 rounded-md font-medium"
            >
              {healthLoading ? "Checking..." : "Refresh Health"}
            </button>
            <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-full shadow-inner">
              <span
                className={`h-2 w-2 rounded-full ${
                  health?.status === "online" ? "bg-emerald-500" : "bg-rose-500"
                } animate-pulse`}
              ></span>
              <span className="text-xs font-medium font-mono text-zinc-300">
                API Status:{" "}
                <span
                  className={
                    health?.status === "online"
                      ? "text-emerald-400 font-semibold"
                      : "text-rose-400 font-semibold"
                  }
                >
                  {health?.status || "offline"}
                </span>
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto px-6 mt-10 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* API Health Detailed Information */}
        <section className="lg:col-span-12 bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 backdrop-blur-sm grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Project Name
            </h3>
            <p className="text-sm font-semibold text-white">{health?.project || "ResumeIQ AI"}</p>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Version / Env
            </h3>
            <p className="text-sm font-semibold text-white font-mono">
              {health ? `v${health.version} (${health.environment})` : "--"}
            </p>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Database Connection
            </h3>
            <p
              className={`text-sm font-semibold capitalize ${
                health?.database === "connected" ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {health?.database || "Disconnected"}
            </p>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              API Connection Endpoint
            </h3>
            <p className="text-xs font-mono text-zinc-300 bg-zinc-950 px-2 py-1 rounded border border-zinc-800 inline-block">
              {BACKEND_URL}
            </p>
          </div>
        </section>

        {/* Step 1: Resume Ingestion Card */}
        <section className="lg:col-span-6 flex flex-col gap-6">
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 flex flex-col flex-1 backdrop-blur-sm shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <span className="h-7 w-7 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center font-mono text-indigo-400 font-bold text-sm">
                1
              </span>
              <h2 className="text-lg font-bold text-white">Ingest Resume Document</h2>
            </div>

            <form onSubmit={handleResumeUpload} className="flex flex-col gap-6 flex-1 justify-between">
              <div className="flex flex-col gap-4">
                <label className="block">
                  <span className="sr-only">Choose Resume File</span>
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-zinc-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700 file:transition-colors file:cursor-pointer cursor-pointer border border-zinc-800 p-2.5 rounded-lg bg-zinc-950/50"
                    required
                  />
                </label>
                <p className="text-[11px] text-zinc-500 font-mono">
                  Supported extensions: .pdf, .docx (Max 10MB)
                </p>

                {resumeError && (
                  <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-xs leading-relaxed">
                    <strong className="font-bold">Error:</strong> {resumeError}
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={!resumeFile || resumeUploading}
                className="w-full h-11 bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg font-semibold text-sm transition-all duration-200 shadow-md shadow-indigo-600/10 flex items-center justify-center gap-2 cursor-pointer mt-4"
              >
                {resumeUploading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing document...
                  </>
                ) : (
                  "Upload & Extract Resume"
                )}
              </button>
            </form>
          </div>

          {/* Resume Upload Output */}
          {resumeResult && (
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 backdrop-blur-sm animate-fadeIn">
              <h3 className="text-sm font-bold text-zinc-200 mb-4 border-b border-zinc-800 pb-2">
                Ingested Resume Metadata
              </h3>
              <div className="grid grid-cols-2 gap-4 text-xs font-mono text-zinc-400 mb-6">
                <div>
                  <span className="text-zinc-500">Record ID:</span>
                  <p className="text-zinc-200 font-semibold truncate" title={resumeResult.id}>
                    {resumeResult.id}
                  </p>
                </div>
                <div>
                  <span className="text-zinc-500">Filename:</span>
                  <p className="text-zinc-200 truncate">{resumeResult.filename}</p>
                </div>
                <div>
                  <span className="text-zinc-500">Type / Size:</span>
                  <p className="text-zinc-200">
                    {resumeResult.file_type} ({(resumeResult.file_size / 1024).toFixed(1)} KB)
                  </p>
                </div>
                <div>
                  <span className="text-zinc-500">Parsed Status:</span>
                  <p className="text-emerald-400 font-semibold uppercase">{resumeResult.status}</p>
                </div>
              </div>

              {resumeResult.parsed_data && (
                <div className="flex flex-col gap-4">
                  <div>
                    <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider mb-2">
                      Candidate Profile
                    </h4>
                    <div className="bg-zinc-950/70 border border-zinc-800/80 rounded-xl p-4 flex flex-col gap-2.5">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-zinc-500">Name</span>
                        <span className="text-zinc-200 font-semibold">
                          {resumeResult.parsed_data.contact_info.name || "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-zinc-500">Email</span>
                        <span className="text-zinc-200 font-semibold font-mono">
                          {resumeResult.parsed_data.contact_info.email || "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-zinc-500">Phone</span>
                        <span className="text-zinc-200 font-semibold font-mono">
                          {resumeResult.parsed_data.contact_info.phone || "N/A"}
                        </span>
                      </div>
                      {(resumeResult.parsed_data.contact_info.linkedin ||
                        resumeResult.parsed_data.contact_info.github) && (
                        <div className="border-t border-zinc-800/60 pt-2.5 mt-1 flex gap-4 text-xs font-mono text-zinc-400">
                          {resumeResult.parsed_data.contact_info.linkedin && (
                            <a
                              href={resumeResult.parsed_data.contact_info.linkedin}
                              target="_blank"
                              rel="noreferrer"
                              className="text-indigo-400 hover:underline truncate"
                            >
                              LinkedIn
                            </a>
                          )}
                          {resumeResult.parsed_data.contact_info.github && (
                            <a
                              href={resumeResult.parsed_data.contact_info.github}
                              target="_blank"
                              rel="noreferrer"
                              className="text-indigo-400 hover:underline truncate"
                            >
                              GitHub
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider mb-2">
                      Extracted NLP Skills ({resumeResult.parsed_data.skills.length})
                    </h4>
                    <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto bg-zinc-950/30 p-3 border border-zinc-800/40 rounded-xl">
                      {resumeResult.parsed_data.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] px-2.5 py-1 rounded-md font-semibold tracking-wide"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {resumeResult.raw_text && (
                    <div>
                      <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider mb-2">
                        Raw Text Preview (First 500 chars)
                      </h4>
                      <pre className="text-[10px] font-mono text-zinc-400 bg-zinc-950 p-3 rounded-xl border border-zinc-850 overflow-x-auto whitespace-pre-wrap max-h-36 overflow-y-auto">
                        {resumeResult.raw_text.slice(0, 500)}
                        {resumeResult.raw_text.length > 500 ? "..." : ""}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </section>

        {/* Step 2: Job Description Card */}
        <section className="lg:col-span-6 flex flex-col gap-6">
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 flex flex-col flex-1 backdrop-blur-sm shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <span className="h-7 w-7 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center font-mono text-purple-400 font-bold text-sm">
                2
              </span>
              <h2 className="text-lg font-bold text-white">Ingest Job Description</h2>
            </div>

            <form onSubmit={handleJdIngest} className="flex flex-col gap-4 flex-1 justify-between">
              <div className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-zinc-400">Job Title</label>
                    <input
                      type="text"
                      placeholder="e.g. Senior Backend Engineer"
                      value={jdTitle}
                      onChange={(e) => setJdTitle(e.target.value)}
                      className="bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-sm text-zinc-100 focus:outline-none focus:border-purple-500 font-medium"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-zinc-400">Company</label>
                    <input
                      type="text"
                      placeholder="e.g. Acme Corp"
                      value={jdCompany}
                      onChange={(e) => setJdCompany(e.target.value)}
                      className="bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-sm text-zinc-100 focus:outline-none focus:border-purple-500 font-medium"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-zinc-400">Job Description Text</label>
                  <textarea
                    rows={6}
                    placeholder="Paste full job description requirements here..."
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    className="bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-sm text-zinc-100 focus:outline-none focus:border-purple-500 font-medium resize-y"
                    required
                  />
                </div>

                {jdError && (
                  <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-xs leading-relaxed">
                    <strong className="font-bold">Error:</strong> {jdError}
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={!jdTitle.trim() || !jdText.trim() || jdIngesting}
                className="w-full h-11 bg-purple-600 hover:bg-purple-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg font-semibold text-sm transition-all duration-200 shadow-md shadow-purple-600/10 flex items-center justify-center gap-2 cursor-pointer mt-4"
              >
                {jdIngesting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Ingesting text...
                  </>
                ) : (
                  "Save & Process Job Description"
                )}
              </button>
            </form>
          </div>

          {/* Job Description Upload Output */}
          {jdResult && (
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 backdrop-blur-sm animate-fadeIn">
              <h3 className="text-sm font-bold text-zinc-200 mb-4 border-b border-zinc-800 pb-2">
                Ingested Job Description Details
              </h3>
              <div className="grid grid-cols-2 gap-4 text-xs font-mono text-zinc-400 mb-4">
                <div>
                  <span className="text-zinc-500">Record ID:</span>
                  <p className="text-zinc-200 font-semibold truncate" title={jdResult.id}>
                    {jdResult.id}
                  </p>
                </div>
                <div>
                  <span className="text-zinc-500">Title / Company:</span>
                  <p className="text-zinc-200 truncate">
                    {jdResult.title} {jdResult.company ? `@ ${jdResult.company}` : ""}
                  </p>
                </div>
              </div>
              <div className="text-xs">
                <span className="font-bold text-zinc-400 block mb-1">Parsed Requirements Status</span>
                <span className="inline-block bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-mono font-semibold">
                  INDEXED & EMBEDDED
                </span>
              </div>
            </div>
          )}
        </section>

        {/* Step 3: Run ATS Matching card */}
        <section className="lg:col-span-12">
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-8 backdrop-blur-sm shadow-xl">
            <div className="flex items-center gap-3 mb-6">
              <span className="h-7 w-7 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center font-mono text-emerald-400 font-bold text-sm">
                3
              </span>
              <h2 className="text-lg font-bold text-white">Evaluate Candidate Alignment</h2>
            </div>

            {/* Run controls / weights config */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-zinc-800 pb-6 mb-6">
              <div className="grid grid-cols-3 gap-4 max-w-lg flex-1">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-zinc-400">Skills Match Weight</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1.0"
                    value={skillsWeight}
                    onChange={(e) => setSkillsWeight(parseFloat(e.target.value) || 0.0)}
                    className="bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500 font-mono font-semibold"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-zinc-400">Semantic Weight</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1.0"
                    value={semanticWeight}
                    onChange={(e) => setSemanticWeight(parseFloat(e.target.value) || 0.0)}
                    className="bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500 font-mono font-semibold"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-zinc-400">Experience Weight</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1.0"
                    value={experienceWeight}
                    onChange={(e) => setExperienceWeight(parseFloat(e.target.value) || 0.0)}
                    className="bg-zinc-950 border border-zinc-800 rounded-lg p-2 text-sm text-zinc-100 focus:outline-none focus:border-emerald-500 font-mono font-semibold"
                  />
                </div>
              </div>

              <div className="flex-shrink-0">
                <button
                  type="button"
                  onClick={handleEvaluateMatch}
                  disabled={!resumeResult?.id || !jdResult?.id || matchEvaluating}
                  className="w-full md:w-56 h-12 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:from-zinc-800 disabled:to-zinc-800 disabled:text-zinc-500 text-white rounded-lg font-bold text-sm transition-all duration-200 shadow-lg shadow-emerald-600/10 flex items-center justify-center gap-2 cursor-pointer"
                >
                  {matchEvaluating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Evaluating...
                    </>
                  ) : (
                    "Run ATS Matching Engine"
                  )}
                </button>
                {!resumeResult?.id && !jdResult?.id && (
                  <p className="text-[10px] text-zinc-500 mt-2 text-center">
                    Upload resume and JD first.
                  </p>
                )}
              </div>
            </div>

            {matchError && (
              <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl text-xs mb-6">
                <strong className="font-bold">Error:</strong> {matchError}
              </div>
            )}

            {/* Match results layout */}
            {matchResult && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fadeIn">
                
                {/* Big Score Visualizer */}
                <div className="lg:col-span-4 bg-zinc-950/60 border border-zinc-800 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                  <span className="text-xs font-bold tracking-wider text-zinc-400 uppercase mb-4">
                    Overall ATS Fit Score
                  </span>
                  
                  {/* Circular visualizer */}
                  <div className="relative flex items-center justify-center h-40 w-40">
                    <svg className="absolute w-full h-full transform -rotate-90">
                      <circle
                        cx="80"
                        cy="80"
                        r="68"
                        stroke="#27272a"
                        strokeWidth="10"
                        fill="transparent"
                      />
                      <circle
                        cx="80"
                        cy="80"
                        r="68"
                        stroke="url(#emeraldGradient)"
                        strokeWidth="10"
                        fill="transparent"
                        strokeDasharray={2 * Math.PI * 68}
                        strokeDashoffset={2 * Math.PI * 68 * (1 - matchResult.overall_score / 100)}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                      <defs>
                        <linearGradient id="emeraldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#10b981" />
                          <stop offset="100%" stopColor="#14b8a6" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <span className="text-4xl font-extrabold text-white tracking-tight">
                      {matchResult.overall_score.toFixed(0)}
                      <span className="text-xl text-zinc-500 font-normal">%</span>
                    </span>
                  </div>

                  <p className="text-xs text-zinc-400 max-w-[200px] mt-6 leading-relaxed">
                    Composite score weighted from skills alignment, experience, and semantic matching.
                  </p>
                </div>

                {/* Score breakdown per category */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                  <div>
                    <h3 className="text-sm font-bold text-zinc-200 mb-3 uppercase tracking-wider">
                      Metric Breakdown
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      
                      {/* Skills match */}
                      <div className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-xl flex flex-col gap-2">
                        <span className="text-xs font-semibold text-zinc-400">Skills Match Score</span>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold text-emerald-400">
                            {matchResult.skills_score?.toFixed(1) || "--"}
                          </span>
                          <span className="text-xs text-zinc-500 font-mono">/100</span>
                        </div>
                        <div className="w-full bg-zinc-800 rounded-full h-1.5">
                          <div
                            className="bg-emerald-500 h-1.5 rounded-full"
                            style={{ width: `${matchResult.skills_score || 0}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Semantic match */}
                      <div className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-xl flex flex-col gap-2">
                        <span className="text-xs font-semibold text-zinc-400">Semantic Similarity</span>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold text-teal-400">
                            {matchResult.education_score?.toFixed(1) || "--"}
                          </span>
                          <span className="text-xs text-zinc-500 font-mono">/100</span>
                        </div>
                        <div className="w-full bg-zinc-800 rounded-full h-1.5">
                          <div
                            className="bg-teal-500 h-1.5 rounded-full"
                            style={{ width: `${matchResult.education_score || 0}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Experience Match */}
                      <div className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-xl flex flex-col gap-2">
                        <span className="text-xs font-semibold text-zinc-400">Experience Alignment</span>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold text-sky-400">
                            {matchResult.experience_score?.toFixed(1) || "--"}
                          </span>
                          <span className="text-xs text-zinc-500 font-mono">/100</span>
                        </div>
                        <div className="w-full bg-zinc-800 rounded-full h-1.5">
                          <div
                            className="bg-sky-500 h-1.5 rounded-full"
                            style={{ width: `${matchResult.experience_score || 0}%` }}
                          ></div>
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* Skills Alignment Match Details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Matched Skills */}
                    <div className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-xl">
                      <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-3">
                        Matched Skills ({matchResult.matched_skills?.skills.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                        {matchResult.matched_skills?.skills.length ? (
                          matchResult.matched_skills.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[10px] px-2 py-0.5 rounded font-mono font-semibold"
                            >
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-zinc-500 italic">No skills matched.</span>
                        )}
                      </div>
                    </div>

                    {/* Missing Skills */}
                    <div className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-xl">
                      <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block mb-3">
                        Missing Skills ({matchResult.missing_skills?.skills.length || 0})
                      </span>
                      <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                        {matchResult.missing_skills?.skills.length ? (
                          matchResult.missing_skills.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="bg-rose-500/10 border border-rose-500/20 text-rose-300 text-[10px] px-2 py-0.5 rounded font-mono font-semibold"
                            >
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-emerald-500 italic">No missing skills!</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Gemini AI Executive Summary Feedback */}
                  <div className="bg-zinc-950/60 border border-zinc-800 p-6 rounded-2xl">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block mb-3">
                      Gemini AI Suitability Feedback
                    </span>
                    <div className="text-xs text-zinc-300 leading-relaxed font-sans bg-zinc-950 p-5 rounded-xl border border-zinc-850/60 shadow-inner">
                      {renderMarkdown(matchResult.breakdown?.ai_feedback || "No feedback generated.")}
                    </div>
                  </div>

                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
