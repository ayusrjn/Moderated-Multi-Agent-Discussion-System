from enum import Enum
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

class DiscussionPhase(str, Enum):
    INTRODUCTION = "Introduction"
    ARGUMENTATION = "Argumentation"
    SYNTHESIS = "Synthesis"
    CONCLUSION = "Conclusion"

class AgentRole(str, Enum):
    SKEPTIC = "Analytical Skeptic"
    PROPONENT = "Constructive Proponent"
    MODERATOR = "Moderator"

class Turn(BaseModel):
    turn_number: int
    speaker: str
    content: str
    phase: DiscussionPhase

class ViolationLog(BaseModel):
    agent_name: str
    turn_number: int
    violation_type: str
    description: str

class AgentProfile(BaseModel):
    name: str
    role: AgentRole
    epistemic_stance: str
    system_prompt: str

class ConversationState(BaseModel):
    topic: str
    turn_number: int = 0
    active_speaker: Optional[str] = None
    discussion_phase: DiscussionPhase = DiscussionPhase.INTRODUCTION
    history: List[Turn] = []
    violations: Dict[str, int] = {}
    
    def log_turn(self, speaker: str, content: str):
        self.turn_number += 1
        self.history.append(Turn(
            turn_number=self.turn_number,
            speaker=speaker,
            content=content,
            phase=self.discussion_phase
        ))

    def log_violation(self, agent_name: str, type: str, desc: str):
        current_count = self.violations.get(agent_name, 0)
        self.violations[agent_name] = current_count + 1
