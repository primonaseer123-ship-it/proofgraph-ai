import io
import time
import uuid
from typing import List, Dict, Any
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import CollectorOutputManifest, IngestedArtifactItem
from app.core.security import compute_sha256
from pypdf import PdfReader
from docx import Document

class CollectorAgent(BaseProofGraphAgent):
    """
    Collector Agent: Ingests documents (PDF, DOCX, Code, Text), extracts textual content,
    calculates cryptographic SHA-256 checksums, and records provenance offsets.
    """
    def __init__(self):
        super().__init__(name="collector_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            raw_inputs: List[Dict[str, Any]] = context.state.get("raw_inputs", [])
            ingested_items: List[IngestedArtifactItem] = []
            total_tokens = 0
            warnings = []

            for item in raw_inputs:
                filename = item.get("filename", "unknown_artifact.txt")
                source_type = item.get("source_type", "manual")
                data_bytes = item.get("data_bytes", b"")
                
                if isinstance(data_bytes, str):
                    data_bytes = data_bytes.encode("utf-8")

                sha256 = compute_sha256(data_bytes)
                extracted_text = ""

                # Extract text based on file type
                if filename.lower().endswith(".pdf") or source_type == "pdf":
                    try:
                        reader = PdfReader(io.BytesIO(data_bytes))
                        text_parts = [page.extract_text() or "" for page in reader.pages]
                        extracted_text = "\n".join(text_parts)
                    except Exception as e:
                        warnings.append(f"PDF extraction warning for {filename}: {str(e)}")
                        extracted_text = data_bytes.decode("utf-8", errors="ignore")
                elif filename.lower().endswith(".docx") or source_type == "docx":
                    try:
                        doc = Document(io.BytesIO(data_bytes))
                        extracted_text = "\n".join([p.text for p in doc.paragraphs])
                    except Exception as e:
                        warnings.append(f"DOCX extraction warning for {filename}: {str(e)}")
                        extracted_text = data_bytes.decode("utf-8", errors="ignore")
                else:
                    extracted_text = data_bytes.decode("utf-8", errors="ignore")

                approx_tokens = len(extracted_text.split())
                total_tokens += approx_tokens

                ingested_items.append(IngestedArtifactItem(
                    artifact_id=f"art_{uuid.uuid4().hex[:12]}",
                    source_type=source_type,
                    sha256_checksum=sha256,
                    original_file_name=filename,
                    byte_size=len(data_bytes),
                    raw_text=extracted_text,
                    metadata={"approx_tokens": approx_tokens, "timestamp": time.time()}
                ))

            manifest = CollectorOutputManifest(
                user_id=context.user_id,
                artifacts=ingested_items,
                total_tokens_extracted=total_tokens,
                warnings=warnings
            )

            context.state["collector_manifest"] = manifest
            return self.record_success(start_time, manifest, warnings)

        except Exception as e:
            return self.record_failure(start_time, f"CollectorAgent failure: {str(e)}")
