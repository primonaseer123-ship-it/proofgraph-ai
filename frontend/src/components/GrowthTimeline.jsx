import React from "react";
import { TrendingUp, Milestone, Sparkles, Award } from "lucide-react";

export default function GrowthTimeline({ growthData }) {
  if (!growthData || !growthData.stages || growthData.stages.length === 0) {
    return (
      <div className="p-8 border border-slate-800 rounded-2xl bg-slate-900/40 text-center text-slate-500 text-xs">
        Run the multi-agent pipeline to generate your temporal skill trajectory.
      </div>
    );
  }

  return (
    <div className="border border-slate-800 rounded-2xl bg-slate-900/60 p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-400" />
            Verified Growth & Competency Trajectory
          </h3>
          <p className="text-xs text-slate-400">
            Temporal evolution of demonstrated skills across academic semesters and projects.
          </p>
        </div>
        <span className="text-xs px-3 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 font-mono">
          Velocity: {growthData.learning_velocity}
        </span>
      </div>

      {/* Timeline Steps */}
      <div className="relative pl-6 space-y-8 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gradient-to-b before:from-blue-500 before:via-indigo-500 before:to-emerald-500">
        {growthData.stages.map((stage, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline Marker Dot */}
            <div className="absolute -left-[27px] top-1.5 w-4 h-4 rounded-full bg-slate-950 border-2 border-indigo-400 group-hover:scale-125 transition-transform" />

            <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-950/60 hover:border-slate-700 transition-all shadow-md">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-1 mb-2">
                <span className="text-xs font-mono font-bold text-indigo-400">{stage.period}</span>
                <span className="text-[11px] text-slate-400 font-medium">Complexity: {stage.complexity_level}</span>
              </div>

              <h4 className="text-sm font-bold text-slate-200">{stage.title}</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{stage.narrative}</p>

              <div className="mt-3 flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/60">
                {stage.skills_demonstrated.map((skill, sIdx) => (
                  <span
                    key={sIdx}
                    className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-800/90 text-slate-300 border border-slate-700"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Focus Areas & Recommendations */}
      {growthData.recommended_focus_areas && (
        <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-800/40 text-xs">
          <div className="flex items-center gap-2 font-bold text-blue-300 mb-1.5">
            <Sparkles className="w-4 h-4" /> Recommended Growth Horizons:
          </div>
          <div className="flex flex-wrap gap-2 text-slate-300">
            {growthData.recommended_focus_areas.map((rec, rIdx) => (
              <span key={rIdx} className="px-2.5 py-1 rounded-lg bg-blue-900/30 border border-blue-700/50">
                → {rec}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
