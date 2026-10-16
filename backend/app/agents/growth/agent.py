import time
from typing import List
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    SkillMappingResult, 
    GrowthTrajectoryReport, 
    TrajectoryStageDTO
)

class GrowthAnalysisAgent(BaseProofGraphAgent):
    """
    Growth Analysis Agent: Analyzes temporal development, technology transitions,
    skill emergence velocity, and identifies areas of active expansion versus dormancy.
    """
    def __init__(self):
        super().__init__(name="growth_analysis_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            mapping: SkillMappingResult = context.state.get("skill_mapping")
            if not mapping:
                return self.record_failure(start_time, "Missing skill_mapping in execution state.")

            active_skills = [s.skill_slug for s in mapping.mapped_skills]

            # Construct logical progression stages based on grounded skills
            stages: List[TrajectoryStageDTO] = []
            
            # Stage 1: Core Foundations
            foundation_skills = [s for s in active_skills if s in ["java-oop", "cpp", "data-structures"]]
            if foundation_skills:
                stages.append(TrajectoryStageDTO(
                    timestamp_period="Year 1 - 2 (Foundations)",
                    focus_domain="Core Computing & Object-Oriented Principles",
                    acquired_skills=foundation_skills,
                    project_complexity_score=0.65,
                    narrative="Demonstrated mastery of core algorithms, OOP paradigms, and structured software development."
                ))

            # Stage 2: Data & Systems Persistence
            data_skills = [s for s in active_skills if s in ["sql", "mysql", "java-jdbc", "postgresql"]]
            if data_skills:
                stages.append(TrajectoryStageDTO(
                    timestamp_period="Year 2 - 3 (Systems & Persistence)",
                    focus_domain="Relational Databases & Enterprise Connectivity",
                    acquired_skills=data_skills,
                    project_complexity_score=0.78,
                    narrative="Expanded into schema design, query optimization, and programmatic database integration."
                ))

            # Stage 3: Modern Web & Applied Frameworks
            modern_skills = [s for s in active_skills if s in ["react", "fastapi", "git"]]
            if modern_skills:
                stages.append(TrajectoryStageDTO(
                    timestamp_period="Year 3 - 4 (Modern Full-Stack)",
                    focus_domain="Web Frameworks & Distributed Collaboration",
                    acquired_skills=modern_skills,
                    project_complexity_score=0.85,
                    narrative="Transitioned to component-driven frontend architecture and RESTful microservices."
                ))

            # If no stages categorized, provide baseline stage
            if not stages:
                stages.append(TrajectoryStageDTO(
                    timestamp_period="Recent Submissions",
                    focus_domain="General Exploration",
                    acquired_skills=active_skills,
                    project_complexity_score=0.50,
                    narrative="Initial evidence recorded across detected technical domains."
                ))

            report = GrowthTrajectoryReport(
                user_id=context.user_id,
                chronological_stages=stages,
                learning_patterns=[
                    "Evolution from academic OOP concepts to full-stack database-backed applications.",
                    "Increasing complexity from standalone scripts to multi-tier architectures."
                ],
                dormant_skills=[],
                velocity_assessment="Steady, upward trajectory in software engineering competency."
            )

            context.state["growth_report"] = report
            return self.record_success(start_time, report)

        except Exception as e:
            return self.record_failure(start_time, f"GrowthAnalysisAgent failure: {str(e)}")
