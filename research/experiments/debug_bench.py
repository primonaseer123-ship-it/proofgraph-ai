import json
import asyncio
from pathlib import Path
from app.agents.supervisor.orchestrator import ProofGraphSupervisor

DATASET_PATH = Path(__file__).resolve().parent.parent / "datasets" / "synthetic_profiles.json"

async def debug_profiles():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    supervisor = ProofGraphSupervisor()
    for p in data["profiles"]:
        print(f"\n--- Checking Profile: {p['name']} ({p['id']}) ---")
        raw_inputs = [
            {
                "filename": art["title"] + ".txt",
                "source_type": art["type"],
                "data_bytes": art["text"].encode("utf-8")
            } for art in p["artifacts"]
        ]
        user_claims = [
            {
                "skill_slug": c["skill_slug"],
                "stated_proficiency": c["stated_proficiency"],
                "claim_text": c["claim_text"]
            } for c in p["claims"]
        ]

        res = await supervisor.execute_pipeline(
            user_id=p["id"],
            raw_inputs=raw_inputs,
            user_claims=user_claims,
            db=None
        )

        print("Extracted techs:", [t for item in res["extracted_evidence"].evidence_items for t in item.extracted_technologies])
        print("Mapped skills:", [s.skill_slug for s in res["skill_mapping"].mapped_skills])
        print("Verifications:", [(e.skill_slug, e.status.value, e.composite_strength_score) for e in res["verification_report"].evaluations])
        print("Contradictions:", [(c.inconsistency_type, c.claim_text) for c in res["contradiction_report"].contradictions_found])

if __name__ == "__main__":
    asyncio.run(debug_profiles())
