import time
import re
import uuid
from typing import List
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    CollectorOutputManifest, 
    ExtractedEvidenceBatch, 
    ExtractedEvidenceItemDTO, 
    GroundedSnippetProvenance
)

# Pattern definitions for concrete evidence grounding
TECH_PATTERNS = [
    {
        "pattern": r"(class\s+\w+\s+extends\s+\w+|interface\s+\w+|implements\s+\w+|abstract\s+class)",
        "tech": "Java OOP",
        "behavior": "Demonstrated Object-Oriented Programming (inheritance/interfaces/abstract classes)"
    },
    {
        "pattern": r"(DriverManager\.getConnection|PreparedStatement|ResultSet|import\s+java\.sql)",
        "tech": "JDBC",
        "behavior": "Database connectivity and relational query execution via JDBC"
    },
    {
        "pattern": r"(CREATE\s+TABLE|SELECT\s+.*?\s+FROM|INSERT\s+INTO|FOREIGN\s+KEY|JOIN\s+\w+)",
        "tech": "SQL",
        "behavior": "Relational schema definition and relational SQL queries"
    },
    {
        "pattern": r"(import\s+React|useState|useEffect|export\s+default\s+function|const\s+\[.*?\]\s*=\s*useState)",
        "tech": "React",
        "behavior": "Frontend state management and component lifecycle in React"
    },
    {
        "pattern": r"(FastAPI|APIRouter|@app\.(get|post|put|delete)|from\s+fastapi\s+import)",
        "tech": "FastAPI",
        "behavior": "RESTful API route definition and backend web services"
    },
    {
        "pattern": r"(torch\.|tensorflow\.|keras\.|fit\(|predict\(|Sequential\(|train_test_split)",
        "tech": "Machine Learning",
        "behavior": "Model training, architecture definition, or inference pipeline"
    },
    {
        "pattern": r"(git\s+commit|git\s+push|Merge\s+pull\s+request|branch)",
        "tech": "Git",
        "behavior": "Version control, branching, or commit history"
    },
    {
        "pattern": r"(def\s+\w+\(.*?\)|\bimport\s+(os|sys|json|math)\b)",
        "tech": "Python Scripting",
        "behavior": "Python function definition and modular automation"
    }
]

class EvidenceExtractionAgent(BaseProofGraphAgent):
    """
    Evidence Extraction Agent: Analyzes collected text/code chunks, isolates concrete
    actions and technical behaviors, and preserves exact character offsets and line numbers.
    """
    def __init__(self):
        super().__init__(name="evidence_extraction_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            manifest: CollectorOutputManifest = context.state.get("collector_manifest")
            if not manifest:
                return self.record_failure(start_time, "Missing collector_manifest in execution state.")

            extracted_items: List[ExtractedEvidenceItemDTO] = []

            for artifact in manifest.artifacts:
                text = artifact.raw_text
                lines = text.split("\n")

                for rule in TECH_PATTERNS:
                    matches = list(re.finditer(rule["pattern"], text, re.IGNORECASE))
                    for m in matches[:3]: # Take up to 3 highest quality grounded snippets per pattern
                        start_char = m.start()
                        end_char = m.end()

                        # Determine snippet context (up to 3 surrounding lines)
                        line_no = text[:start_char].count("\n") + 1
                        snippet_start_line = max(0, line_no - 2)
                        snippet_end_line = min(len(lines), line_no + 2)
                        context_snippet = "\n".join(lines[snippet_start_line:snippet_end_line]).strip()
                        if not context_snippet:
                            context_snippet = m.group(0)

                        extracted_items.append(ExtractedEvidenceItemDTO(
                            evidence_id=f"ev_{uuid.uuid4().hex[:10]}",
                            artifact_id=artifact.artifact_id,
                            activity_name=f"{rule['tech']} in {artifact.original_file_name}",
                            demonstrated_behavior=rule["behavior"],
                            extracted_technologies=[rule["tech"]],
                            evidence_date=None,
                            provenance=GroundedSnippetProvenance(
                                artifact_id=artifact.artifact_id,
                                start_char_idx=start_char,
                                end_char_idx=end_char,
                                line_start=snippet_start_line + 1,
                                line_end=snippet_end_line,
                                raw_text=context_snippet
                            ),
                            directness_score=0.9 if "class " in context_snippet or "def " in context_snippet else 0.75,
                            confidence_score=0.88
                        ))

            # If no regex match found but text exists, extract paragraph summaries
            if not extracted_items and manifest.artifacts:
                for art in manifest.artifacts:
                    if len(art.raw_text.strip()) > 20:
                        first_para = art.raw_text.strip().split("\n\n")[0][:300]
                        extracted_items.append(ExtractedEvidenceItemDTO(
                            evidence_id=f"ev_{uuid.uuid4().hex[:10]}",
                            artifact_id=art.artifact_id,
                            activity_name=f"General Activity in {art.original_file_name}",
                            demonstrated_behavior="Documented academic or practical activity",
                            extracted_technologies=[],
                            evidence_date=None,
                            provenance=GroundedSnippetProvenance(
                                artifact_id=art.artifact_id,
                                start_char_idx=0,
                                end_char_idx=len(first_para),
                                line_start=1,
                                line_end=min(5, len(art.raw_text.split('\n'))),
                                raw_text=first_para
                            ),
                            directness_score=0.4,
                            confidence_score=0.6
                        ))

            batch = ExtractedEvidenceBatch(
                user_id=context.user_id,
                evidence_items=extracted_items
            )
            context.state["extracted_evidence"] = batch
            return self.record_success(start_time, batch)

        except Exception as e:
            return self.record_failure(start_time, f"EvidenceExtractionAgent failure: {str(e)}")
