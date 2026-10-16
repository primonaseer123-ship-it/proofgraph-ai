import React, { useState } from "react";
import { UploadCloud, FileText, Code2, Play, CheckCircle2, Loader2, PlusCircle } from "lucide-react";

export default function EvidenceUploadHub({ onUploadFile, onManualSubmit, onRunPipeline, runningPipeline }) {
  const [activeTab, setActiveTab] = useState("file"); // "file" | "manual" | "claim"
  const [uploadFile, setUploadFile] = useState(null);
  const [sourceType, setSourceType] = useState("project_report");
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Manual form state
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [technologies, setTechnologies] = useState("Java, OOP, JDBC, MySQL");
  const [evidenceDate, setEvidenceDate] = useState("2025-11-20");

  const handleFileSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploading(true);
    try {
      await onUploadFile(uploadFile, sourceType);
      setUploadSuccess(true);
      setUploadFile(null);
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (!title || !rawText) return;
    setUploading(true);
    try {
      const techList = technologies.split(",").map(t => t.trim()).filter(Boolean);
      await onManualSubmit(title, rawText, techList, evidenceDate);
      setUploadSuccess(true);
      setTitle("");
      setRawText("");
      setTimeout(() => setUploadSuccess(false), 3000);
    } catch (err) {
      alert(`Submission failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border border-slate-800 rounded-2xl bg-slate-900/60 p-6 shadow-xl space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-blue-400" />
            Evidence Ingestion & Multi-Agent Execution Hub
          </h3>
          <p className="text-xs text-slate-400">
            Submit academic project reports, transcripts, or code repositories for cryptographic verification.
          </p>
        </div>

        <button
          onClick={onRunPipeline}
          disabled={runningPipeline}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
        >
          {runningPipeline ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Running 8-Agent Pipeline...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              Run Multi-Agent Verification
            </>
          )}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-3 text-xs font-semibold">
        <button
          onClick={() => setActiveTab("file")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "file"
              ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
              : "bg-slate-800/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Upload PDF / DOCX
        </button>
        <button
          onClick={() => setActiveTab("manual")}
          className={`px-4 py-2 rounded-xl transition-all ${
            activeTab === "manual"
              ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
              : "bg-slate-800/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          Paste Code / Project Report
        </button>
      </div>

      {uploadSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> Evidence artifact cryptographically digested and added to ingestion pool!
        </div>
      )}

      {/* File Upload Mode */}
      {activeTab === "file" && (
        <form onSubmit={handleFileSubmit} className="space-y-4">
          <div className="border-2 border-dashed border-slate-700/80 hover:border-blue-500 rounded-xl p-8 text-center bg-black/20 transition-all">
            <input
              type="file"
              id="evidence-file"
              accept=".pdf,.docx,.txt,.java,.py,.sql"
              className="hidden"
              onChange={(e) => setUploadFile(e.target.files[0])}
            />
            <label htmlFor="evidence-file" className="cursor-pointer flex flex-col items-center">
              <FileText className="w-10 h-10 text-slate-400 mb-2" />
              <span className="text-sm font-semibold text-slate-200">
                {uploadFile ? uploadFile.name : "Click to browse or drop document"}
              </span>
              <span className="text-xs text-slate-500 mt-1">
                Supports PDF, DOCX, Code Files (Java, Python, SQL) up to 50MB
              </span>
            </label>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3 w-full md:w-auto">
              <label className="text-xs text-slate-400 whitespace-nowrap">Artifact Type:</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="text-xs bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none"
              >
                <option value="project_report">Project Report</option>
                <option value="transcript">University Transcript</option>
                <option value="certificate">Verified Certificate</option>
                <option value="github_repo">Git Archive / Repository</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={!uploadFile || uploading}
              className="w-full md:w-auto px-5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white disabled:opacity-40 transition-all"
            >
              {uploading ? "Digesting..." : "Ingest & Compute SHA-256"}
            </button>
          </div>
        </form>
      )}

      {/* Manual Code / Report Mode */}
      {activeTab === "manual" && (
        <form onSubmit={handleManualSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Project / Activity Title:</label>
              <input
                type="text"
                required
                placeholder="e.g. Distributed Database Assignment"
                className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Associated Technologies (comma-separated):</label>
              <input
                type="text"
                placeholder="Java, MySQL, JDBC"
                className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
                value={technologies}
                onChange={(e) => setTechnologies(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Completion Date:</label>
              <input
                type="date"
                className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
                value={evidenceDate}
                onChange={(e) => setEvidenceDate(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Code Snippets & Architecture Details:</label>
            <textarea
              required
              rows={6}
              placeholder="Paste code snippets, class definitions, SQL schemas, or architectural reports here..."
              className="w-full text-xs font-mono bg-slate-950 border border-slate-700 rounded-lg p-3 text-slate-200 focus:outline-none focus:border-blue-500"
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploading}
              className="px-5 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 transition-all shadow-md"
            >
              {uploading ? "Recording..." : "Save to Evidence Pool"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
