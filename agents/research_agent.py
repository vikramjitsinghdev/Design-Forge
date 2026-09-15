import os
import json
import requests
from dotenv import load_dotenv

from pexel_service import PexelsService


load_dotenv()


class ResearchAgent:
    """
    Research Agent for DesignForge.

    Responsibilities:
        1. Receive DesignRequirements from InputAgent.
        2. Use Ollama GPT 120B to create a ResearchPlan.
        3. Send the ResearchPlan search queries to PexelsService.
        4. Return the ResearchPlan + image references.

    The Research Agent does NOT directly communicate with
    the Pexels API. PexelsService handles all API communication.
    """

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self):

        self.api_key = os.getenv("OLLAMA_API_KEY")

        self.base_url = os.getenv(
            "OLLAMA_URL",
            "https://ollama.com/api/chat"
        )

        self.model = os.getenv(
            "OLLAMA_RESEARCH_MODEL",
            "gpt-oss:120b-cloud"
        )

        if not self.api_key:
            raise ValueError(
                "OLLAMA_API_KEY is missing from .env"
            )

        # Pexels service
        self.pexels = PexelsService()

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    # ---------------------------------------------------------
    # MAIN METHOD
    # ---------------------------------------------------------

    def research(self, design_requirements):
        """
        Main Research Agent pipeline.

        Input:
            DesignRequirements dictionary from InputAgent.

        Output:
            {
                "research_plan": {...},
                "image_results": {...}
            }
        """

        if not isinstance(design_requirements, dict):
            raise TypeError(
                "design_requirements must be a dictionary"
            )

        # ---------------------------------------------
        # STEP 1
        # Generate Research Plan
        # ---------------------------------------------

        print("\n[ResearchAgent] Generating research plan...")

        research_plan = self._generate_research_plan(
            design_requirements
        )

        print("[ResearchAgent] Research plan generated.")

        # ---------------------------------------------
        # STEP 2
        # Send Research Plan to Pexels
        # ---------------------------------------------

        print("\n[ResearchAgent] Sending queries to Pexels...")

        image_results = self.pexels.search_research_plan(
            research_plan,
            primary_per_query=4,
            alternative_per_query=2,
            max_results=20
        )

        print(
            f"[ResearchAgent] "
            f"Retrieved {image_results['total_results']} images."
        )

        # ---------------------------------------------
        # STEP 3
        # Combine Results
        # ---------------------------------------------

        return {
            "research_plan": research_plan,
            "image_results": image_results
        }

    # ---------------------------------------------------------
    # GENERATE RESEARCH PLAN
    # ---------------------------------------------------------

    def _generate_research_plan(self, design_requirements):
        """
        Ask Ollama GPT 120B to convert DesignRequirements
        into a structured ResearchPlan.
        """

        system_prompt = """
You are the Research Agent for DesignForge.

Your job is to transform structured design requirements
into a focused visual research plan.

You are NOT responsible for:
- Calling APIs
- Searching the web
- Retrieving images
- Accessing databases
- Ranking individual images

PexelsService will use your search queries to retrieve
visual references.

Your job is ONLY to determine:
- What should be searched
- What visual attributes matter
- What requirements are important
- What must be excluded
- What preferences should influence research
- How visual diversity should be represented

IMPORTANT:

1. Only use information contained in the DesignRequirements.
2. Do not invent requirements.
3. Do not turn every preference into a hard requirement.
4. Hard requirements should only contain clearly mandatory
   requirements.
5. Hard exclusions should contain explicit exclusions.
6. Search queries should be concise and visually searchable.
7. Generate multiple different search queries.
8. Avoid duplicate search queries.
9. Do not include URLs.
10. Return ONLY valid JSON.

Return exactly this structure:

{
    "research_objective": "",
    "primary_search_queries": [],
    "alternative_search_queries": [],
    "visual_attributes": [],
    "ranking_priorities": [],
    "hard_requirements": [],
    "hard_exclusions": [],
    "soft_preferences": [],
    "diversity_categories": []
}
"""

        user_prompt = f"""
Create a research plan from these DesignRequirements:

{json.dumps(design_requirements, indent=4)}
"""

        payload = {
            "model": self.model,

            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            "stream": False,

            "format": "json",

            "options": {
                "temperature": 0.1
            }
        }

        try:

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

        except requests.exceptions.RequestException as e:

            raise RuntimeError(
                f"Ollama Research Agent request failed: {e}"
            )

        # ---------------------------------------------
        # Extract model response
        # ---------------------------------------------

        try:

            content = data["message"]["content"]

        except (KeyError, TypeError):

            raise RuntimeError(
                "Unexpected response format from Ollama."
            )

        # ---------------------------------------------
        # Parse JSON
        # ---------------------------------------------

        try:

            research_plan = json.loads(content)

        except json.JSONDecodeError:

            raise RuntimeError(
                "Research Agent returned invalid JSON."
            )

        # ---------------------------------------------
        # Validate Research Plan
        # ---------------------------------------------

        self._validate_research_plan(
            research_plan
        )

        return research_plan

    # ---------------------------------------------------------
    # VALIDATE RESEARCH PLAN
    # ---------------------------------------------------------

    def _validate_research_plan(self, research_plan):
        """
        Make sure the Research Agent returned all
        required fields.
        """

        required_fields = [
            "research_objective",
            "primary_search_queries",
            "alternative_search_queries",
            "visual_attributes",
            "ranking_priorities",
            "hard_requirements",
            "hard_exclusions",
            "soft_preferences",
            "diversity_categories"
        ]

        if not isinstance(research_plan, dict):

            raise ValueError(
                "Research plan must be a dictionary."
            )

        missing_fields = [
            field
            for field in required_fields
            if field not in research_plan
        ]

        if missing_fields:

            raise ValueError(
                "Research plan is missing fields: "
                + ", ".join(missing_fields)
            )

        # Fields that should contain lists
        list_fields = [
            "primary_search_queries",
            "alternative_search_queries",
            "visual_attributes",
            "ranking_priorities",
            "hard_requirements",
            "hard_exclusions",
            "soft_preferences",
            "diversity_categories"
        ]

        for field in list_fields:

            if not isinstance(
                research_plan[field],
                list
            ):

                raise ValueError(
                    f"Research plan field '{field}' "
                    f"must be a list."
                )

        # Objective must be a string
        if not isinstance(
            research_plan["research_objective"],
            str
        ):

            raise ValueError(
                "research_objective must be a string."
            )

        # At least one search query is required
        if not research_plan["primary_search_queries"]:

            raise ValueError(
                "Research Agent did not generate "
                "any primary search queries."
            )

    # ---------------------------------------------------------
    # OPTIONAL: RESEARCH PLAN ONLY
    # ---------------------------------------------------------

    def generate_research_plan(self, design_requirements):
        """
        Generate only the ResearchPlan.

        Useful for testing the AI separately without
        calling Pexels.
        """

        return self._generate_research_plan(
            design_requirements
        )