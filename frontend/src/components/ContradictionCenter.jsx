import React, { useState } from "react";
import { AlertOctagon, CheckCircle2, ShieldAlert, ArrowRight, CornerDownRight } from "lucide-react";

export default function ContradictionCenter({ contradictions, onResolve }) {
  const [resolutionNotes, setResolutionNotes] = useState({});
  const [loadingId, setLoadingId] = useState(null);

  if (!contradictions || contradictions.length === 0) {
    return (
      <div className="p-8 border border-emerald-900/50 rounded-2xl bg-emerald-950/20 text-center">
        <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
        <h3 className="text-base font-bold text-emerald-200">No Active Contradictions Detected</h3>
        <p className="text-xs text-emerald-400/80 mt-1 max-w-md mx-auto">
          Your active claims are consistent with your submitted project evidence and academic milestones.
        </p>
      </div>
    );
  }

  const handleResolveSubmit = async (id) => {
    const note = resolutionNotes[id] || "User acknowledged discrepancy and adjusted profile assertion.";
    setLoadingId(id);
    try {
      if (onResolve) await onResolve(id, note);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-rose-400" />
          Contradiction & Discrepancy Center ({contradictions.length})
        </h3>
        <span className="text-xs px-2.5 py-1 rounded-full bg-rose-950 text-rose-300 border border-rose-800 font-mono">
          Audit Flags
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {contradictions.map((ctd) => (
          <div
            key={ctd.id}
            className="p-5 rounded-2xl border border-rose-900/60 bg-gradient-to-r from-rose-950/30 via-slate-900/80 to-slate-900 border-l-4 border-l-rose-500 shadow-xl"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-rose-900/50 text-rose-300 font-bold">
                  {ctd.contradiction_type} • Severity: {ctd.severity}
                </span>
                <h4 className="text-sm font-bold text-slate-100 mt-2">
                  {ctd.claim_text || "Unsubstantiated Profile Assertion"}
                </h4>
              </div>
            </div>

            <p className="text-xs text-slate-300 mt-3 leading-relaxed bg-black/40 p-3 rounded-lg border border-slate-800">
              <strong className="text-rose-400 block mb-1">Formal Audit Explanation:</strong>
              {ctd.explanation}
            </p>

            <div className="mt-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
              <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <CornerDownRight className="w-3.5 h-3.5 text-blue-400" />
                <span>Recommended Action: <strong className="text-slate-200">Adjust stated proficiency or provide repository.</strong></span>
              </div>

              {!ctd.is_resolved ? (
                <div className="flex items-center gap-2 w-full md:w-auto">
                  <input
                    type="text"
                    placeholder="Enter resolution explanation..."
                    className="text-xs bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 w-full md:w-64"
                    value={resolutionNotes[ctd.id] || ""}
                    onChange={(e) => setResolutionNotes({ ...resolutionNotes, [ctd.id]: e.target.value })}
                  />
                  <button
                    onClick={() => handleResolveSubmit(ctd.id)}
                    disabled={loadingId === ctd.id}
                    className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white transition-all whitespace-nowrap disabled:opacity-50"
                  >
                    {loadingId === ctd.id ? "Resolving..." : "Acknowledge"}
                  </button>
                </div>
              ) : (
                <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Resolved
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
