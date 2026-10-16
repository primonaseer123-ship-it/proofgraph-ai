from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.claim import Claim
from app.models.skill import Skill
from app.models.evidence import EvidenceItem, EvidenceSource, ClaimEvidenceLink
from app.models.contradiction import Contradiction
from app.schemas.graph_dtos import GraphResponse, ReactFlowNode, ReactFlowEdge, ReactFlowPosition

class GraphService:
    """
    Graph Service: Traverses relational evidence nodes and constructs a typed,
    hierarchical DAG formatted for React Flow canvas rendering.
    """
    @staticmethod
    async def build_user_graph(user_id: str, db: AsyncSession) -> GraphResponse:
        nodes: List[ReactFlowNode] = []
        edges: List[ReactFlowEdge] = []

        # 1. Fetch User
        u_res = await db.execute(select(User).where(User.id == user_id))
        user = u_res.scalars().first()
        if not user:
            return GraphResponse(nodes=[], edges=[], stats={})

        user_node_id = f"node_user_{user.id}"
        nodes.append(ReactFlowNode(
            id=user_node_id,
            type="userNode",
            position=ReactFlowPosition(x=450, y=50),
            data={
                "label": user.full_name,
                "institution": user.institution or "FAST-NUCES",
                "degree": user.degree_program or "BS Computer Science",
                "role": user.role
            }
        ))

        # 2. Fetch Claims
        c_res = await db.execute(select(Claim).where(Claim.user_id == user_id))
        claims = c_res.scalars().all()

        # 3. Fetch Contradictions for flagging
        ctd_res = await db.execute(select(Contradiction).where(Contradiction.user_id == user_id, Contradiction.is_resolved == False))
        contradictions = ctd_res.scalars().all()
        flagged_claim_ids = {c.claim_id for c in contradictions if c.claim_id}

        # 4. Fetch Evidence Items
        ev_source_res = await db.execute(select(EvidenceSource).where(EvidenceSource.user_id == user_id))
        sources = ev_source_res.scalars().all()
        source_ids = [s.id for s in sources]

        evidence_items = []
        if source_ids:
            ev_item_res = await db.execute(select(EvidenceItem).where(EvidenceItem.source_id.in_(source_ids)))
            evidence_items = ev_item_res.scalars().all()

        # Place Claim Nodes (Level 1: y=200)
        claim_x_start = 50
        claim_spacing = 260
        for idx, claim in enumerate(claims):
            c_node_id = f"node_claim_{claim.id}"
            is_flagged = claim.id in flagged_claim_ids

            nodes.append(ReactFlowNode(
                id=c_node_id,
                type="claimNode",
                position=ReactFlowPosition(x=claim_x_start + (idx * claim_spacing), y=200),
                data={
                    "claim_id": claim.id,
                    "skill_slug": claim.skill_slug,
                    "stated_proficiency": claim.stated_proficiency,
                    "claim_text": claim.claim_text,
                    "status": claim.current_status,
                    "confidence": claim.confidence_score,
                    "is_flagged": is_flagged,
                    "justification": claim.justification_summary
                }
            ))

            # Edge from User -> Claim
            edges.append(ReactFlowEdge(
                id=f"edge_{user_node_id}_{c_node_id}",
                source=user_node_id,
                target=c_node_id,
                label="asserts",
                animated=is_flagged,
                style={"stroke": "#ef4444" if is_flagged else "#3b82f6", "strokeWidth": 2}
            ))

        # Place Evidence Nodes (Level 2: y=380)
        ev_x_start = 80
        ev_spacing = 240
        for idx, ev in enumerate(evidence_items):
            ev_node_id = f"node_ev_{ev.id}"
            nodes.append(ReactFlowNode(
                id=ev_node_id,
                type="evidenceNode",
                position=ReactFlowPosition(x=ev_x_start + (idx * ev_spacing), y=380),
                data={
                    "evidence_id": ev.id,
                    "title": ev.title,
                    "skill_slug": ev.skill_slug,
                    "raw_snippet": ev.raw_snippet[:160] + "...",
                    "directness": ev.directness_score,
                    "strength": ev.strength_score,
                    "status": ev.verification_status
                }
            ))

        # Connect Claims to Evidence via Links
        links_res = await db.execute(select(ClaimEvidenceLink))
        links = links_res.scalars().all()
        for link in links:
            c_node_id = f"node_claim_{link.claim_id}"
            ev_node_id = f"node_ev_{link.evidence_item_id}"
            edges.append(ReactFlowEdge(
                id=f"edge_link_{link.id}",
                source=c_node_id,
                target=ev_node_id,
                label="substantiated by",
                style={"stroke": "#10b981", "strokeWidth": 2}
            ))

        # Place Sources (Level 3: y=560)
        src_x_start = 120
        src_spacing = 280
        for idx, src in enumerate(sources):
            src_node_id = f"node_src_{src.id}"
            nodes.append(ReactFlowNode(
                id=src_node_id,
                type="sourceNode",
                position=ReactFlowPosition(x=src_x_start + (idx * src_spacing), y=560),
                data={
                    "source_id": src.id,
                    "source_type": src.source_type,
                    "name": src.original_name,
                    "sha256": src.file_sha256[:12] + "...",
                    "bytes": src.byte_size
                }
            ))

            # Connect Evidence -> Source
            for ev in [e for e in evidence_items if e.source_id == src.id]:
                ev_node_id = f"node_ev_{ev.id}"
                edges.append(ReactFlowEdge(
                    id=f"edge_src_{ev_node_id}_{src_node_id}",
                    source=ev_node_id,
                    target=src_node_id,
                    label="extracted from",
                    style={"stroke": "#6b7280", "strokeDasharray": "5,5"}
                ))

        stats = {
            "total_claims": len(claims),
            "verified_claims": len([c for c in claims if c.current_status in ["EVIDENCE_SUPPORTED", "HUMAN_VERIFIED"]]),
            "unsupported_claims": len([c for c in claims if c.current_status == "UNSUPPORTED"]),
            "evidence_items": len(evidence_items),
            "sources_count": len(sources),
            "active_contradictions": len(contradictions)
        }

        return GraphResponse(nodes=nodes, edges=edges, stats=stats)
