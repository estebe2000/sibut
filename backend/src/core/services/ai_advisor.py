from openai import OpenAI
import os

class AIAdvisor:
    def __init__(self):
        self.api_key = os.environ.get('AI_API_KEY')
        self.api_url = os.environ.get('AI_API_URL')
        self.model = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')

        if self.api_key and self.api_url:
             self.client = OpenAI(
                 base_url=self.api_url,
                 api_key=self.api_key
             )
        else:
            self.client = None

    def suggest_acs(self, activity_description, acs_list):
        """
        Suggests relevant ACs based on activity description.
        acs_list: List of dicts {code: str, description: str}
        """
        if not self.client:
            return {"error": "AI not configured"}

        # Prepare prompt
        acs_text = "\n".join([f"- {ac['code']}: {ac['description']}" for ac in acs_list])

        prompt = f"""
        You are a pedagogical assistant. Given the following activity description, identify which Critical Learnings (AC) from the provided list are most relevant.

        Activity Description:
        "{activity_description}"

        Available ACs:
        {acs_text}

        Return ONLY a JSON list of relevant AC codes, e.g., ["AC11.01", "AC12.02"].
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful pedagogical assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            # Cleanup basic json markdown
            content = content.replace('```json', '').replace('```', '').strip()
            return content
        except Exception as e:
            return {"error": str(e)}
