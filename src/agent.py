import os
import google.generativeai as genai
from .models import AgentProfile
from .prompts import SYSTEM_PROMPT_TEMPLATE

class LLMAgent:
    def __init__(self, profile: AgentProfile, model_name: str = "gemini-3-flash-preview"):
        self.profile = profile
        self.model = genai.GenerativeModel(model_name)
        self.chat = None # Initialize history later

    def start_new_session(self, topic: str, phase: str):
        """Initializes a new chat session with the system prompt."""
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            name=self.profile.name,
            role=self.profile.role.value,
            stance=self.profile.epistemic_stance,
            topic=topic,
            phase=phase
        )
        # In Gemini API, system instruction is best passed at model creation or as first message.
        # For simplicity in this stateful loop, we'll start history with it as a user message 
        # that frames the context, or use system_instruction if available in this lib version.
        
        # Re-initializing model with system instruction if supported would be ideal, 
        # but let's stick to prepending context for robustness across versions.
        
        self.chat = self.model.start_chat(history=[
            {"role": "user", "parts": [f"SYSTEM INSTRUCTION:\n{system_prompt}"]}
        ])
        
        # Consume the model's acknowledgment to "prime" it (optional, but good for role adherence)
        # self.chat.send_message("Acknowledge your role.") 
        # We might skip this to save latency and just assume it works on next user prompt.

    def generate_response(self, context_message: str):
        if not self.chat:
            raise ValueError("Chat session not started. Call start_new_session first.")
        
        try:
            response = self.chat.send_message(context_message)
            return response.text.strip()
        except Exception as e:
            return f"[ERROR generating response: {e}]"
