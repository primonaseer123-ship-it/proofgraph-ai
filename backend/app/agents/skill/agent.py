import time
from typing import List, Dict
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import ExtractedEvidenceBatch, SkillMappingResult, MappedSkillNodeDTO

TAXONOMY_MAPPING: Dict[str, Dict[str, str]] = {
    "Java": {
        "slug": "java",
        "name": "Java",
        "category": "Languages",
        "path": "Software Development/Languages/Java"
    },
    "Java OOP": {
        "slug": "java-oop",
        "name": "Object-Oriented Programming (Java)",
        "category": "Languages",
        "path": "Software Development/Languages/Java/OOP"
    },
    "JDBC": {
        "slug": "java-jdbc",
        "name": "JDBC & Database Integration",
        "category": "Languages",
        "path": "Software Development/Languages/Java/JDBC"
    },
    "SQL": {
        "slug": "sql",
        "name": "SQL & Relational Databases",
        "category": "Databases",
        "path": "Databases/Relational/SQL"
    },
    "MySQL": {
        "slug": "mysql",
        "name": "MySQL",
        "category": "Databases",
        "path": "Databases/Relational/MySQL"
    },
    "React": {
        "slug": "react",
        "name": "React.js",
        "category": "Web",
        "path": "Web Development/Frontend/React"
    },
    "FastAPI": {
        "slug": "fastapi",
        "name": "FastAPI",
        "category": "Backend",
        "path": "Web Development/Backend/FastAPI"
    },
    "Machine Learning": {
        "slug": "machine-learning",
        "name": "Machine Learning",
        "category": "Data Science",
        "path": "Data Science/Machine Learning"
    },
    "Git": {
        "slug": "git",
        "name": "Git & Version Control",
        "category": "DevOps",
        "path": "DevOps/Version Control/Git"
    },
    "Python": {
        "slug": "python",
        "name": "Python",
        "category": "Languages",
        "path": "Software Development/Languages/Python"
    },
    "Python Scripting": {
        "slug": "python-scripting",
        "name": "Python Scripting & Automation",
        "category": "Languages",
        "path": "Software Development/Languages/Python/Scripting"
    }
}

PARENT_SKILL_MAP: Dict[str, str] = {
    "java-oop": "java",
    "java-jdbc": "java",
    "mysql": "sql",
    "postgresql": "sql",
    "python-scripting": "python"
}

class SkillMappingAgent(BaseProofGraphAgent):
    """
    Skill Mapping Agent: Connects raw extracted technical indicators to the standardized
    hierarchical skill ontology, grouping evidence items under canonical skill slugs and
    propagating evidence up parent taxonomy relationships.
    """
    def __init__(self):
        super().__init__(name="skill_mapping_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            batch: ExtractedEvidenceBatch = context.state.get("extracted_evidence")
            if not batch:
                return self.record_failure(start_time, "Missing extracted_evidence in execution state.")

            skill_evidence_map: Dict[str, List[str]] = {}
            unmapped = []

            for item in batch.evidence_items:
                for tech in item.extracted_technologies:
                    if tech in TAXONOMY_MAPPING:
                        slug = TAXONOMY_MAPPING[tech]["slug"]
                        if slug not in skill_evidence_map:
                            skill_evidence_map[slug] = []
                        skill_evidence_map[slug].append(item.evidence_id)

                        # Propagate evidence to parent skill in taxonomy hierarchy
                        parent_slug = PARENT_SKILL_MAP.get(slug)
                        if parent_slug:
                            if parent_slug not in skill_evidence_map:
                                skill_evidence_map[parent_slug] = []
                            skill_evidence_map[parent_slug].append(item.evidence_id)
                    else:
                        unmapped.append(tech)

            mapped_nodes: List[MappedSkillNodeDTO] = []
            for slug, ev_ids in skill_evidence_map.items():
                meta = next((v for v in TAXONOMY_MAPPING.values() if v["slug"] == slug), None)
                if meta:
                    mapped_nodes.append(MappedSkillNodeDTO(
                        skill_slug=slug,
                        canonical_name=meta["name"],
                        taxonomy_category=meta["category"],
                        taxonomy_path=meta["path"],
                        substantiating_evidence_ids=list(set(ev_ids)),
                        mapping_confidence=0.95
                    ))

            result = SkillMappingResult(
                user_id=context.user_id,
                mapped_skills=mapped_nodes,
                unmapped_raw_mentions=list(set(unmapped))
            )

            context.state["skill_mapping"] = result
            return self.record_success(start_time, result)

        except Exception as e:
            return self.record_failure(start_time, f"SkillMappingAgent failure: {str(e)}")
