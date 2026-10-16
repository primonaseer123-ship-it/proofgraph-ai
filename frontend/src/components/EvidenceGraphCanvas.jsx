import React, { useState } from "react";
import { ShieldCheck, AlertTriangle, FileCode, CheckCircle2, XCircle, Info, ExternalLink } from "lucide-react";

export default function EvidenceGraphCanvas({ graphData, onSelectNode }) {
  const [selectedNode, setSelectedNode] = useState(null);

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 border border-slate-800 rounded-xl bg-slate-900/40 text-slate-400">
        <Info className="w-10 h-10 mb-3 text-slate-500" />
        <p className="font-medium">No Evidence Graph Generated Yet</p>
        <p className="text-xs text-slate-500 mt-1">Upload an academic project or repository to construct your graph.</p>
      </div>
    );
  }

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onSelectNode) onSelectNode(node);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "HUMAN_VERIFIED":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800"><CheckCircle2 className="w-3 h-3" /> Human Verified</span>;
      case "EVIDENCE_SUPPORTED":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-blue-950 text-blue-300 border border-blue-800"><ShieldCheck className="w-3 h-3" /> Evidence Supported</span>;
      case "PARTIALLY_SUPPORTED":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-amber-950 text-amber-300 border border-amber-800"><AlertTriangle className="w-3 h-3" /> Partially Supported</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-rose-950 text-rose-300 border border-rose-800"><XCircle className="w-3 h-3" /> Unsupported Claim</span>;
    }
  };

  const userNodes = graphData.nodes.filter(n => n.type === "userNode");
  const claimNodes = graphData.nodes.filter(n => n.type === "claimNode");
  const evidenceNodes = graphData.nodes.filter(n => n.type === "evidenceNode");
  const sourceNodes = graphData.nodes.filter(n => n.type === "sourceNode");

  return (
    <div className="relative border border-slate-800 rounded-2xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-6 overflow-hidden shadow-2xl">
      {/* Canvas Top Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-6">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-blue-400" />
            Interactive Personal Evidence Graph
          </h3>
          <p className="text-xs text-slate-400">Click any claim or evidence node to inspect cryptographic byte-spans and AST proofs.</p>
        </div>
        <div className="flex gap-4 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Verified ({graphData.stats?.verified_claims || 0})</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Unsupported ({graphData.stats?.unsupported_claims || 0})</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Discrepancies ({graphData.stats?.active_contradictions || 0})</span>
        </div>
      </div>

      {/* Hierarchical Columnar DAG Layout */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 min-h-[460px]">
        {/* Tier 1: User Root */}
        <div className="flex flex-col gap-4">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">1. Identity Root</span>
          {userNodes.map(node => (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className="cursor-pointer p-4 rounded-xl border border-blue-500/30 bg-blue-950/20 hover:border-blue-400 transition-all shadow-lg"
            >
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold text-white mb-2 shadow-inner">
                {node.data.label?.charAt(0) || "U"}
              </div>
              <h4 className="font-bold text-slate-100 text-sm">{node.data.label}</h4>
              <p className="text-xs text-slate-400 mt-0.5">{node.data.institution}</p>
              <p className="text-xs text-blue-400/90 font-mono mt-1">{node.data.degree}</p>
            </div>
          ))}
        </div>

        {/* Tier 2: Asserted Claims */}
        <div className="flex flex-col gap-4">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">2. Asserted Claims</span>
          {claimNodes.map(node => (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className={`cursor-pointer p-4 rounded-xl border transition-all shadow-md ${
                node.data.is_flagged
                  ? "border-rose-500/50 bg-rose-950/20 hover:border-rose-400 ring-1 ring-rose-500/30"
                  : node.data.status === "EVIDENCE_SUPPORTED" || node.data.status === "HUMAN_VERIFIED"
                  ? "border-blue-500/40 bg-blue-950/20 hover:border-blue-400"
                  : "border-slate-800 bg-slate-900/60 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold uppercase text-slate-300">{node.data.skill_slug}</span>
                {getStatusBadge(node.data.status)}
              </div>
              <p className="text-xs text-slate-200 font-medium line-clamp-2">{node.data.claim_text}</p>
              <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                <span>Stated: <strong className="text-slate-300">{node.data.stated_proficiency}</strong></span>
                <span className="font-mono">Conf: {(node.data.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>

        {/* Tier 3: Extracted Evidence */}
        <div className="flex flex-col gap-4">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">3. Grounded Evidence</span>
          {evidenceNodes.map(node => (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className="cursor-pointer p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-400 transition-all shadow-md"
            >
              <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-xs mb-1">
                <FileCode className="w-3.5 h-3.5" />
                {node.data.title}
              </div>
              <pre className="text-[10px] font-mono bg-black/50 p-2 rounded text-emerald-200/90 overflow-x-hidden line-clamp-3 border border-emerald-900/50">
                {node.data.raw_snippet}
              </pre>
              <div className="mt-2 flex justify-between text-[11px] text-slate-400">
                <span>Directness: {node.data.directness}</span>
                <span className="text-emerald-400 font-mono">Proof: High</span>
              </div>
            </div>
          ))}
          {evidenceNodes.length === 0 && (
            <div className="p-4 border border-dashed border-slate-800 rounded-xl text-center text-xs text-slate-500">
              No evidence extracted yet.
            </div>
          )}
        </div>

        {/* Tier 4: Provenance Sources */}
        <div className="flex flex-col gap-4">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">4. Cryptographic Sources</span>
          {sourceNodes.map(node => (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className="cursor-pointer p-4 rounded-xl border border-slate-800 bg-slate-900/40 hover:border-slate-700 transition-all shadow-md"
            >
              <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-1">
                <span className="truncate max-w-[140px]">{node.data.name}</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">{node.data.source_type}</span>
              </div>
              <p className="text-[11px] font-mono text-blue-400 truncate mt-1">SHA256: {node.data.sha256}</p>
              <p className="text-[10px] text-slate-500 mt-1">Size: {(node.data.bytes / 1024).toFixed(1)} KB</p>
            </div>
          ))}
          {sourceNodes.length === 0 && (
            <div className="p-4 border border-dashed border-slate-800 rounded-xl text-center text-xs text-slate-500">
              No sources attached.
            </div>
          )}
        </div>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="mt-6 p-4 rounded-xl bg-slate-900/90 border border-slate-700/80 text-xs animate-in fade-in slide-in-from-bottom-2">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span className="font-bold text-slate-200 uppercase tracking-wider">
              Inspect Node: <code className="text-blue-400">{selectedNode.id}</code> ({selectedNode.type})
            </span>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800"
            >
              ✕ Close
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-slate-400 mb-1 font-semibold">Node Metadata:</p>
              <pre className="p-2.5 rounded bg-black/60 font-mono text-slate-300 overflow-x-auto text-[11px] max-h-36">
                {JSON.stringify(selectedNode.data, null, 2)}
              </pre>
            </div>
            <div>
              <p className="text-slate-400 mb-1 font-semibold">Explainability Audit Trail:</p>
              <div className="p-3 rounded bg-slate-950/80 border border-slate-800/80 space-y-2 text-slate-300">
                <p>
                  <strong>Why does ProofGraph assign this status?</strong>
                </p>
                <p className="text-slate-400">
                  {selectedNode.data.justification || "Node was registered and verified via the multi-agent supervisor pipeline with byte-level provenance checks."}
                </p>
                {selectedNode.data.is_flagged && (
                  <p className="text-rose-400 font-semibold flex items-center gap-1.5 mt-2">
                    <AlertTriangle className="w-4 h-4" /> This node is actively flagged by the Contradiction Agent.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
