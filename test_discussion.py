import unittest
import sys
from unittest.mock import MagicMock

# Aggressively mock google.generativeai BEFORE importing controller
mock_genai = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = mock_genai

from src.controller import DiscussionController
from src.models import DiscussionPhase

class TestDiscussionController(unittest.TestCase):
    def setUp(self):
        self.controller = DiscussionController("fake_key")
        
        # Mock agents
        self.controller.agents["AgentA"] = MagicMock()
        self.controller.agents["AgentA"].generate_response.return_value = "Response A"
        self.controller.agents["AgentB"] = MagicMock()
        self.controller.agents["AgentB"].generate_response.return_value = "Response B"

    def test_start_discussion(self):
        msg = self.controller.start_discussion("Test Topic")
        self.assertEqual(self.controller.state.topic, "Test Topic")
        self.assertEqual(self.controller.state.discussion_phase, DiscussionPhase.INTRODUCTION)
        self.controller.agents["AgentA"].start_new_session.assert_called()

    def test_turn_rotation(self):
        self.controller.start_discussion("Test")
        
        # Default order A -> B
        speaker1 = self.controller.next_speaker()
        self.assertEqual(speaker1, "AgentA")
        
        resp1 = self.controller.execute_agent_turn("AgentA")
        self.assertEqual(resp1, "Response A")
        
        speaker2 = self.controller.next_speaker()
        self.assertEqual(speaker2, "AgentB")

    def test_pause_agent(self):
        self.controller.start_discussion("Test")
        self.controller.pause_agent("AgentA")
        
        speaker = self.controller.next_speaker()
        self.assertEqual(speaker, "AgentB") # Should skip A
        
        self.controller.unpause_agent("AgentA")
        # Reset turn index to test A comes back
        self.controller.current_turn_index = 0
        speaker = self.controller.next_speaker()
        self.assertEqual(speaker, "AgentA")

    def test_phase_change(self):
        self.controller.set_phase(DiscussionPhase.ARGUMENTATION)
        self.assertEqual(self.controller.state.discussion_phase, DiscussionPhase.ARGUMENTATION)

if __name__ == '__main__':
    unittest.main()
