import React from "react";
import { Briefcase, ExternalLink, Check, AlertCircle, Info, Building } from "lucide-react";

export default function OpportunityMatcher({ matches }) {
  if (!matches || matches.length === 0) {
    return (
      <div className="p-8 border border-slate-800 rounded-2xl bg-slate-900/40 text-center text-slate-500 text-xs">
        No opportunity matches loaded. Ensure opportunities are seeded and pipeline is run.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-emerald-400" />
            Evidence-Grounded Opportunity Matching
          </h3>
          <p className="text-xs text-slate-400">
            Real internship and fellowship openings evaluated strictly against your substantiated evidence graph.
          </p>
        </div>

        <div className="text-[11px] text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-blue-400" />
          <span>Evidence Alignment Analysis Only</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {matches.map((item) => (
          <div
            key={item.opportunity_id}
            className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all flex flex-col justify-between shadow-xl"
          >
            <div>
              <div className="flex items-start justify-between mb-3">
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                  {item.opportunity_type}
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400">
                  {item.match_percentage}% Match
                </span>
              </div>

              <h4 className="text-sm font-bold text-slate-100 leading-snug">{item.title}</h4>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                <Building className="w-3.5 h-3.5" />
                {item.organization} ({item.location})
              </p>

              {/* Progress bar */}
              <div className="w-full bg-slate-800 rounded-full h-1.5 my-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-emerald-400 h-1.5 rounded-full"
                  style={{ width: `${item.match_percentage}%` }}
                />
              </div>

              {/* Requirements Breakdown */}
              <div className="space-y-2 mt-4">
                <span className="text-[11px] font-semibold text-slate-400 block">Requirement Evidence:</span>
                {item.requirements_breakdown.map((req, rIdx) => (
                  <div
                    key={rIdx}
                    className="flex items-center justify-between text-xs p-2 rounded-lg bg-black/30 border border-slate-800/80"
                  >
                    <span className="font-mono text-slate-300">{req.skill_name || req.skill_slug}</span>
                    {req.matched ? (
                      <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                        <Check className="w-3.5 h-3.5" /> Verified
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-400/90">
                        <AlertCircle className="w-3.5 h-3.5" /> Missing
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[10px] text-slate-500">
                Mandatory: {item.matched_mandatory_count}/{item.total_mandatory_count}
              </span>
              {item.external_url && (
                <a
                  href={item.external_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-semibold"
                >
                  View Role <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
        <Info className="w-4 h-4 text-slate-400 flex-shrink-0" />
        <span>
          <strong>Ethical AI Guardrail:</strong> ProofGraph AI scores evidence presence only. It never guarantees admission, hiring outcomes, or declares absolute candidate superiority.
        </span>
      </div>
    </div>
  );
}
