import unittest
from datetime import datetime

from analyzers.conversation_analyzer import ConversationAnalyzer


class TestConversationAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ConversationAnalyzer(
            openai_api_key="test-key",
            openai_base_url="test-url"
        )

    async def test_analyze_conversation(self):
        result = await self.analyzer.analyze_conversation(
            user_input="이번 주 속초 여행을 가려고 해",
            current_date="2024-11-18"
        )

        self.assertIsNotNone(result)
        self.assertIn("analysis_result", result)
        self.assertIn("user_profile_updates", result)

    async def test_conversation_history(self):
        await self.analyzer.analyze_conversation(
            user_input="이번 주 속초 여행을 가려고 해",
            current_date="2024-11-18"
        )

        history = self.analyzer.get_conversation_history()
        self.assertEqual(len(history), 1)

    async def test_user_profile_update(self):
        await self.analyzer.analyze_conversation(
            user_input="이번 주 속초 여행을 가려고 해",
            current_date="2024-11-18"
        )

        profile = self.analyzer.get_user_profile()
        self.assertGreater(profile["metrics"]["interaction_count"], 0)

if __name__ == '__main__':
    unittest.main()