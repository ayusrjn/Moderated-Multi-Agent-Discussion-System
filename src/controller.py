import json
import time
from typing import Dict, Optional
from .models import ConversationState, AgentProfile, AgentRole, DiscussionPhase, Turn
from .agent import LLMAgent
import google.generativeai as genai


class DiscussionController:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.state = ConversationState(topic="Waiting for topic...")
        self.agents: Dict[str, LLMAgent] = {}
        self._setup_agents()
        
    def _setup_agents(self):
        # Initialize default agents
        profile_a = AgentProfile(
            name="AgentA",
            role=AgentRole.SKEPTIC,
            epistemic_stance="Analytical, skeptical, demands evidence.",
            system_prompt=""
        )
        profile_b = AgentProfile(
            name="AgentB",
            role=AgentRole.PROPONENT,
            epistemic_stance="Constructive, optimistic, focuses on potential.",
            system_prompt=""
        )
        self.agents["AgentA"] = LLMAgent(profile_a)
        self.agents["AgentB"] = LLMAgent(profile_b)
        
        self.turn_order = ["AgentA", "AgentB"]
        self.current_turn_index = 0
        self.paused_agents = set()

    def start_discussion(self, topic: str):
        self.state.topic = topic
        self.state.discussion_phase = DiscussionPhase.INTRODUCTION
        self.state.turn_number = 0
        self.state.history = []
        
        for agent in self.agents.values():
            agent.start_new_session(topic, self.state.discussion_phase.value)
            
        return f"Discussion started on topic: {topic}"

    def next_speaker(self) -> str:
        # Round robin with pause check
        attempts = 0
        while attempts < len(self.turn_order):
            candidate = self.turn_order[self.current_turn_index]
            if candidate not in self.paused_agents:
                return candidate
            self.advance_turn_index()
            attempts += 1
        return "None (All Paused)"

    def advance_turn_index(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def moderator_interject(self, message: str):
        self.state.log_turn("Moderator", message)
        # We need to inject this into agent memory/context effectively
        # For this simple implementation, we assume agents see history or we pass it in next prompt
        return f"Moderator: {message}"

    def execute_agent_turn(self, agent_name: str) -> str:
        agent = self.agents[agent_name]
        
        # specific context construction (this could be improved with full history)
        last_turn = self.state.history[-1] if self.state.history else None
        context = ""
        if last_turn:
            context = f"Last speaker was {last_turn.speaker}: \"{last_turn.content}\".\n"
        
        context += f"It is your turn now, {agent_name}. Discussion Phase: {self.state.discussion_phase.value}."
        
        response = agent.generate_response(context)
        self.state.log_turn(agent_name, response)
        self.advance_turn_index()
        return response

    def set_phase(self, phase: DiscussionPhase):
        self.state.discussion_phase = phase
        return f"Phase changed to {phase.value}"

    def pause_agent(self, agent_name: str):
        if agent_name in self.agents:
            self.paused_agents.add(agent_name)
            return f"Paused {agent_name}."
        return f"Agent {agent_name} not found."

    def unpause_agent(self, agent_name: str):
        if agent_name in self.paused_agents:
            self.paused_agents.remove(agent_name)
            return f"Unpaused {agent_name}."
        return f"{agent_name} was not paused."

    def request_rephrase(self):
        # Rolling back the last turn isn't fully implemented in state,
        # but we can instruct the agent to re-do it.
        # Ideally we pop the last item from history.
        if not self.state.history:
            return "No history to rephrase."
            
        last_turn = self.state.history.pop() # Remove from metrics
        speaker = last_turn.speaker
        
        # We need to tell the agent to try again, perhaps with specific feedback
        return f"Removed last turn from {speaker}. You (Moderator) should now issue an instruction (INTERJECT) and then call NEXT for them to try again."

    def demand_evidence(self, agent_name: str):
        # This is essentially an interjection, but logged specifically
        msg = f"[SYSTEM COMMAND] {agent_name}, provide specific evidence/citations for your last claim."
        self.moderator_interject(msg)
        return f"Demanded evidence from {agent_name}"

    def save_session(self, directory: str = "logs") -> str:
        """Saves current state to a JSON file."""
        import os
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/discussion_{timestamp}.json"
        
        with open(filename, 'w') as f:
            f.write(self.state.model_dump_json(indent=2))
            
        return filename
