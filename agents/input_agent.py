import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class InputAgent:
    """
    Input Agent

    Responsibility:
    - Understand the user's natural-language design request.
    - Extract useful design requirements.
    - Convert the request into structured JSON.
    - Return the structured requirements to the main backend/AI agent.

    This agent does NOT:
    - Search for images.
    - Call Pexels.
    - Rank results.
    - Generate the final design.
    - Access the database.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is missing from the environment variables."
            )

        self.client = Groq(api_key=self.api_key)

        # Keep the model configurable so you can change it
        # without modifying the code.
        self.model = os.getenv(
            "GROQ_INPUT_MODEL",
            "openai/gpt-oss-20b"
        )

    def analyze_input(self, user_input: str) -> dict:
        """
        Analyze the user's natural-language request and convert
        it into structured design requirements.

        Args:
            user_input (str):
                Raw text entered by the user.

        Returns:
            dict:
                Structured design requirements.
        """

        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string.")

        user_input = user_input.strip()

        if not user_input:
            raise ValueError("User input cannot be empty.")

        system_prompt = """
You are the Input Analysis Agent for an AI-powered Design
Inspiration Assistant.

Your ONLY responsibility is to understand what the user wants
and convert their request into structured design requirements.

Do NOT:
- Search the internet.
- Recommend specific products.
- Recommend specific images.
- Invent requirements that the user did not imply.
- Make the final design.
- Rank search results.
- Generate search results.

Your output will be passed to another AI agent that will handle
the main processing, searching, filtering, ranking and explanation.

You must carefully distinguish between:
1. Requirements explicitly stated by the user.
2. Requirements reasonably implied by the user's description.
3. Information the user did not provide.

If something is unknown, use null or an empty list rather than
inventing information.

Return ONLY valid JSON.

Use exactly this structure:

{
    "category": null,
    "purpose": null,
    "audience": null,

    "style": [],
    "colors": [],
    "materials": [],
    "silhouette": [],

    "required_features": [],
    "excluded_features": [],

    "historical_influences": [],
    "functional_requirements": [],

    "complexity": null,
    "manufacturing_method": null,

    "preferred_direction": null,

    "user_preferences": [],
    "special_constraints": [],

    "search_terms": [],

    "confidence": 0.0
}

Field meanings:

category:
The type of design being requested.
Examples:
"jacket", "dress", "chair", "poster", "logo".

purpose:
What the design is intended for.
Examples:
"fashion inspiration", "daily wear", "academic project".

audience:
The intended user/group.
Examples:
"gender-neutral", "teenagers", "professionals".

style:
Visual/design styles explicitly requested or strongly implied.
Examples:
["minimal", "modern", "utility"].

colors:
Requested colors or color palettes.

materials:
Requested or implied materials/textures.

silhouette:
Shape, form, proportions or physical structure.

required_features:
Features that the final inspiration should contain.

excluded_features:
Features that must NOT appear.

historical_influences:
Historical periods, movements or cultural influences.

functional_requirements:
Functional properties the design should satisfy.

complexity:
Requested difficulty or complexity.
Examples:
"beginner", "intermediate", "advanced".

manufacturing_method:
Only provide a manufacturing method if the user explicitly
mentions one. Otherwise use null.

Do NOT infer a manufacturing method from the category.

preferred_direction:
Only provide this if the user explicitly expresses a preference
for familiar, similar, experimental, unconventional, or balanced
design directions. Otherwise use null.

user_preferences:
Other preferences that could affect ranking.

special_constraints:
Any additional restrictions or requirements.

search_terms:
A small list of useful search concepts derived directly
from the user's request. These are NOT final search queries.

confidence:
A number between 0 and 1 representing how clearly the
user's request could be interpreted.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )

            content = response.choices[0].message.content.strip()

            return self._parse_response(content)

        except Exception as e:
            raise RuntimeError(
                f"Input Agent failed to process the request: {e}"
            ) from e

    def _parse_response(self, content: str) -> dict:
        """
        Safely convert the AI response into a Python dictionary.
        """

        # Remove accidental Markdown code fences.
        if content.startswith("```"):
            content = content.replace("```json", "", 1)
            content = content.replace("```", "")
            content = content.strip()

        try:
            result = json.loads(content)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Groq returned invalid JSON:\n{content}"
            ) from e

        self._validate_result(result)

        return result

    def _validate_result(self, result: dict):
        """
        Basic validation to make sure the AI returned the
        structure expected by the rest of the application.
        """

        if not isinstance(result, dict):
            raise ValueError("AI response must be a JSON object.")

        required_fields = [
            "category",
            "purpose",
            "audience",
            "style",
            "colors",
            "materials",
            "silhouette",
            "required_features",
            "excluded_features",
            "historical_influences",
            "functional_requirements",
            "complexity",
            "manufacturing_method",
            "preferred_direction",
            "user_preferences",
            "special_constraints",
            "search_terms",
            "confidence"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in result
        ]

        if missing_fields:
            raise ValueError(
                f"AI response is missing fields: {missing_fields}"
            )

        confidence = result["confidence"]

        if not isinstance(confidence, (int, float)):
            raise ValueError("confidence must be a number.")

        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1.")


# ---------------------------------------------------------
# Simple standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    agent = InputAgent()

    test_input = """
    I want a gender-neutral fall jacket with an oversized
    silhouette. I want dark green and cream colours, utility
    pockets and a simple beginner-friendly construction.
    Avoid visible logos and military styling.
    """

    result = agent.analyze_input(test_input)

    print("\nINPUT AGENT RESULT")
    print("------------------")
    print(json.dumps(result, indent=4))