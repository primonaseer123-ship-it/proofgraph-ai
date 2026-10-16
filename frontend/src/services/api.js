const API_BASE = "http://localhost:8000/api/v1";

let authToken = localStorage.getItem("proofgraph_token") || "";

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    localStorage.setItem("proofgraph_token", token);
  } else {
    localStorage.removeItem("proofgraph_token");
  }
};

export const getAuthToken = () => authToken;

const request = async (endpoint, options = {}) => {
  const headers = { ...options.headers };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}`;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return res.json();
};

export const api = {
  // Auth
  login: async (email, password) => {
    const data = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setAuthToken(data.access_token);
    return data;
  },
  register: async (userData) => {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },
  getMe: () => request("/auth/me"),

  // Graph
  getGraph: () => request("/graph"),
  getGrowthTrajectory: () => request("/graph/growth"),

  // Claims
  getClaims: () => request("/claims"),
  createClaim: (skill_slug, stated_proficiency, claim_text) =>
    request("/claims", {
      method: "POST",
      body: JSON.stringify({ skill_slug, stated_proficiency, claim_text }),
    }),

  // Evidence
  getEvidence: () => request("/evidence"),
  uploadFile: (file, sourceType = "project_report") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_type", sourceType);
    return request("/evidence/upload", {
      method: "POST",
      body: formData,
    });
  },
  createManualEvidence: (title, raw_text, technologies = [], date = null) =>
    request("/evidence/manual", {
      method: "POST",
      body: JSON.stringify({
        title,
        source_type: "project_report",
        raw_text,
        technologies,
        evidence_date: date,
      }),
    }),

  // Pipeline
  runPipeline: () => request("/agents/run", { method: "POST" }),

  // Contradictions
  getContradictions: () => request("/contradictions"),
  resolveContradiction: (id, resolution_note) =>
    request(`/contradictions/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify({ resolution_note }),
    }),

  // Opportunities
  getOpportunities: () => request("/opportunities"),
  getOpportunityMatches: () => request("/opportunities/matches"),

  // Verification
  verifyClaim: (claimId, decision, commentary, amendedProf = null) =>
    request(`/verification/${claimId}/verify`, {
      method: "POST",
      body: JSON.stringify({
        decision,
        commentary,
        amended_proficiency: amendedProf,
      }),
    }),

  // Application Generation
  generateApplication: (target_role, target_company, document_type = "resume") =>
    request("/applications/generate", {
      method: "POST",
      body: JSON.stringify({ target_role, target_company, document_type }),
    }),

  // Research Benchmark
  runBenchmark: () => request("/research/benchmark", { method: "POST" }),
  getSyntheticDataset: () => request("/research/dataset"),
};
