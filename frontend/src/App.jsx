import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Network,
  UploadCloud,
  AlertTriangle,
  TrendingUp,
  Briefcase,
  FileText,
  Beaker,
  UserCheck,
  Sparkles,
  RefreshCw
} from "lucide-react";
import { api, setAuthToken } from "./services/api";
import EvidenceGraphCanvas from "./components/EvidenceGraphCanvas";
import ContradictionCenter from "./components/ContradictionCenter";
import EvidenceUploadHub from "./components/EvidenceUploadHub";
import GrowthTimeline from "./components/GrowthTimeline";
import OpportunityMatcher from "./components/OpportunityMatcher";
import ApplicationGenerator from "./components/ApplicationGenerator";
import ResearchEvaluationPanel from "./components/ResearchEvaluationPanel";

export default function App() {
  const [activeTab, setActiveTab] = useState("graph");
  const [loading, setLoading] = useState(true);
  const [runningPipeline, setRunningPipeline] = useState(false);

  // Core Data State
  const [currentUser, setCurrentUser] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [contradictions, setContradictions] = useState([]);
  const [growthData, setGrowthData] = useState(null);
  const [opportunityMatches, setOpportunityMatches] = useState([]);

  // Auto-authenticate with demo user on initial boot
  useEffect(() => {
    initDemoSession();
  }, []);

  const initDemoSession = async () => {
    setLoading(true);
    try {
      // 1. Attempt login with demo student account
      try {
        const auth = await api.login("hamza.tariq@fast.edu.pk", "Password123!");
        setCurrentUser(auth.user);
      } catch (_) {
        // Register if not found
        await api.register({
          email: "hamza.tariq@fast.edu.pk",
          password: "Password123!",
          full_name: "Hamza Tariq",
          institution: "FAST-NUCES Lahore",
          degree_program: "BS Computer Science",
          role: "student",
          bio: "Undergraduate Computer Science student specializing in backend systems and software engineering."
        });
        const auth = await api.login("hamza.tariq@fast.edu.pk", "Password123!");
        setCurrentUser(auth.user);
      }

      await refreshAllData();
    } catch (err) {
      console.error("Session init failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshAllData = async () => {
    try {
      const [gData, ctdData, grData, oppData] = await Promise.all([
        api.getGraph(),
        api.getContradictions(),
        api.getGrowthTrajectory(),
        api.getOpportunityMatches()
      ]);
      setGraphData(gData);
      setContradictions(ctdData);
      setGrowthData(grData);
      setOpportunityMatches(oppData);
    } catch (err) {
      console.error("Data refresh failed:", err);
    }
  };

  const handleRunPipeline = async () => {
    setRunningPipeline(true);
    try {
      await api.runPipeline();
      await refreshAllData();
      alert("Multi-Agent Pipeline executed successfully! Evidence Graph updated.");
    } catch (err) {
      alert(`Pipeline error: ${err.message}`);
    } finally {
      setRunningPipeline(false);
    }
  };

  const handleUploadFile = async (file, sourceType) => {
    await api.uploadFile(file, sourceType);
    await refreshAllData();
  };

  const handleManualSubmit = async (title, rawText, technologies, date) => {
    await api.createManualEvidence(title, rawText, technologies, date);
    await refreshAllData();
  };

  const handleResolveContradiction = async (id, note) => {
    await api.resolveContradiction(id, note);
    await refreshAllData();
  };

  const handleGenerateApplication = async (role, company, docType) => {
    return api.generateApplication(role, company, docType);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center text-slate-400 font-mono text-xs">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-blue-500" />
        Initializing ProofGraph AI Environment & Knowledge Engine...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-600/30">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-tight text-white">ProofGraph AI</h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800">
                v1.0 Research Edition
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">“Don't just tell the world what you can do. Prove it.”</p>
          </div>
        </div>

        {/* User Badge & Pipeline Status */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-3 pr-4 border-r border-slate-800 text-xs">
            <div className="text-right">
              <div className="font-bold text-slate-200">{currentUser?.full_name || "Hamza Tariq"}</div>
              <div className="text-[11px] text-slate-400">{currentUser?.institution || "FAST-NUCES"}</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-blue-400 text-xs">
              HT
            </div>
          </div>

          <button
            onClick={refreshAllData}
            title="Refresh Evidence Graph"
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition-all"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap gap-2 p-1.5 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <button
            onClick={() => setActiveTab("graph")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "graph"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Network className="w-4 h-4" /> Evidence Graph
          </button>
          <button
            onClick={() => setActiveTab("ingest")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "ingest"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <UploadCloud className="w-4 h-4" /> Evidence Ingestion
          </button>
          <button
            onClick={() => setActiveTab("contradictions")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "contradictions"
                ? "bg-rose-600 text-white shadow-md shadow-rose-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            Contradictions ({contradictions.length})
          </button>
          <button
            onClick={() => setActiveTab("growth")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "growth"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <TrendingUp className="w-4 h-4" /> Growth Trajectory
          </button>
          <button
            onClick={() => setActiveTab("opportunities")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "opportunities"
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Briefcase className="w-4 h-4" /> Opportunity Matcher
          </button>
          <button
            onClick={() => setActiveTab("applications")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "applications"
                ? "bg-teal-600 text-white shadow-md shadow-teal-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-4 h-4" /> Zero-Hallucination Resume
          </button>
          <button
            onClick={() => setActiveTab("research")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === "research"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Beaker className="w-4 h-4" /> Research Mode
          </button>
        </nav>

        {/* Tab Content Panes */}
        {activeTab === "graph" && (
          <EvidenceGraphCanvas graphData={graphData} />
        )}

        {activeTab === "ingest" && (
          <EvidenceUploadHub
            onUploadFile={handleUploadFile}
            onManualSubmit={handleManualSubmit}
            onRunPipeline={handleRunPipeline}
            runningPipeline={runningPipeline}
          />
        )}

        {activeTab === "contradictions" && (
          <ContradictionCenter
            contradictions={contradictions}
            onResolve={handleResolveContradiction}
          />
        )}

        {activeTab === "growth" && (
          <GrowthTimeline growthData={growthData} />
        )}

        {activeTab === "opportunities" && (
          <OpportunityMatcher matches={opportunityMatches} />
        )}

        {activeTab === "applications" && (
          <ApplicationGenerator
            onGenerate={handleGenerateApplication}
            generating={false}
          />
        )}

        {activeTab === "research" && (
          <ResearchEvaluationPanel />
        )}
      </div>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800/80 py-4 text-center text-xs text-slate-500 font-mono">
        ProofGraph AI • Autonomous Multi-Agent Evidence Intelligence Architecture • Rule: NO EVIDENCE → NO FACTUAL CLAIM
      </footer>
    </div>
  );
}
