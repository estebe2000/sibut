from unittest.mock import MagicMock, patch
from django.test import TestCase
from core.services.ai_advisor import AIAdvisor

class AIAdvisorTest(TestCase):
    @patch('core.services.ai_advisor.OpenAI')
    def test_suggest_acs(self, mock_openai):
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '["AC11.01"]'
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value = mock_completion

        # Setup env vars handled in __init__?
        # We need to ensure os.environ has values or we pass them?
        # The class uses os.environ. Let's patch dict.
        with patch.dict('os.environ', {'AI_API_KEY': 'test', 'AI_API_URL': 'http://test'}):
            advisor = AIAdvisor()
            result = advisor.suggest_acs("Test description", [{'code': 'AC11.01', 'description': 'Desc'}])

            self.assertEqual(result, '["AC11.01"]')
            mock_instance.chat.completions.create.assert_called_once()
