import React, { useState } from "react";
import { FileCheck, Copy, Check, ShieldCheck, EyeOff, Sparkles } from "lucide-react";

export default function ApplicationGenerator({ onGenerate, generating }) {
  const [targetRole, setTargetRole] = useState("Junior Backend Engineer");
  const [targetCompany, setTargetCompany] = useState("Systems Limited");
  const [docType, setDocType] = useState("resume");
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await onGenerate(targetRole, targetCompany, docType);
    setResult(data);
  };

  const handleCopy = () => {
    if (!result?.markdown_content) return;
    navigator.clipboard.writeText(result.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-emerald-400" />
            Zero-Hallucination Application Generator
          </h3>
          <p className="text-xs text-slate-400">
            Produces tailored resumes where every bullet point is provably grounded in verified evidence.
          </p>
        </div>
      </div>

      {/* Generator Form */}
      <form onSubmit={handleSubmit} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-4 items-end shadow-xl">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Target Job / Scholarship:</label>
          <input
            type="text"
            required
            className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Target Organization:</label>
          <input
            type="text"
            required
            className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
            value={targetCompany}
            onChange={(e) => setTargetCompany(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Document Format:</label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full text-xs bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200"
          >
            <option value="resume">Evidence-Linked Resume</option>
            <option value="statement">Personal Statement</option>
            <option value="cover_letter">Technical Motivation Letter</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={generating}
          className="w-full py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-600/30 flex items-center justify-center gap-1.5"
        >
          {generating ? "Auditing Evidence..." : "Generate Verified Resume"}
        </button>
      </form>

      {/* Output Display */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Markdown Viewer */}
          <div className="md:col-span-2 p-6 rounded-2xl bg-black/40 border border-slate-800 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <span className="text-xs font-mono font-bold text-slate-400 uppercase">
                Generated Markdown Capsule ({result.document_type})
              </span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? "Copied!" : "Copy Markdown"}
              </button>
            </div>

            <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-[500px] overflow-y-auto">
              {result.markdown_content}
            </pre>
          </div>

          {/* Verification Audit Sidecar */}
          <div className="space-y-4">
            {/* Grounded Citations */}
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-lg">
              <h4 className="text-xs font-bold text-slate-200 flex items-center gap-1.5 mb-3">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Grounded Proof Citations ({result.grounded_citations.length})
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {result.grounded_citations.map((cite, cIdx) => (
                  <div key={cIdx} className="p-2.5 rounded-lg bg-black/40 border border-slate-800 text-[11px]">
                    <div className="flex justify-between font-mono text-emerald-400">
                      <span>[{cite.evidence_id.slice(0, 8)}]</span>
                      <span className="text-slate-500">{cite.source_name}</span>
                    </div>
                    <p className="text-slate-300 mt-1 truncate">{cite.claim_text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Omitted Unsupported Claims */}
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-rose-900/50 shadow-lg">
              <h4 className="text-xs font-bold text-rose-300 flex items-center gap-1.5 mb-2">
                <EyeOff className="w-4 h-4 text-rose-400" /> Omitted Unsupported Claims ({result.unsupported_claims_omitted.length})
              </h4>
              <p className="text-[11px] text-slate-400 mb-2 leading-relaxed">
                ProofGraph strictly filtered out these user claims because no concrete code or project evidence was submitted:
              </p>
              <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                {result.unsupported_claims_omitted.map((omitted, oIdx) => (
                  <div key={oIdx} className="p-2 rounded bg-rose-950/20 border border-rose-900/40 text-[11px] text-rose-300 font-mono">
                    ✕ {omitted}
                  </div>
                ))}
                {result.unsupported_claims_omitted.length === 0 && (
                  <span className="text-[11px] text-slate-500">None. All asserted claims had verified proof.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
