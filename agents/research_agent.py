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
        3. Send the ResearchPlan to PexelsService.
        4. Receive raw and filtered image results.
        5. Return the complete research results.

    The Research Agent does NOT:
        - Directly communicate with the Pexels API.
        - Filter images itself.
        - Rank images.
        - Analyze image pixels.
        - Access the database.
        - Search the web directly.
    """

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self):

        self.api_key = os.getenv(
            "OLLAMA_API_KEY"
        )

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

        # PexelsService handles:
        # Pexels API → FilterService
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

        Pipeline:

            DesignRequirements
                    ↓
            ResearchPlan
                    ↓
            PexelsService
                    ↓
            Raw Images
                    ↓
            FilterService
                    ↓
            Filtered Images

        Output:
            {
                "research_plan": {...},
                "image_results": {
                    "raw_results": {...},
                    "filtered_results": {...}
                }
            }
        """

        if not isinstance(
            design_requirements,
            dict
        ):
            raise TypeError(
                "design_requirements must be a dictionary"
            )

        # -----------------------------------------------------
        # STEP 1
        # Generate Research Plan
        # -----------------------------------------------------

        print(
            "\n[ResearchAgent] "
            "Generating research plan..."
        )

        research_plan = (
            self._generate_research_plan(
                design_requirements
            )
        )

        print(
            "[ResearchAgent] "
            "Research plan generated."
        )

        # -----------------------------------------------------
        # STEP 2
        # Send Research Plan to PexelsService
        # -----------------------------------------------------

        print(
            "\n[ResearchAgent] "
            "Sending queries to Pexels..."
        )

        image_results = (
            self.pexels.search_research_plan(
                research_plan,
                primary_per_query=4,
                alternative_per_query=2,
                max_results=20
            )
        )

        # -----------------------------------------------------
        # STEP 3
        # Validate PexelsService Response
        # -----------------------------------------------------

        if not isinstance(
            image_results,
            dict
        ):
            raise RuntimeError(
                "PexelsService returned "
                "an invalid response."
            )

        raw_results = image_results.get(
            "raw_results"
        )

        filtered_results = image_results.get(
            "filtered_results"
        )

        if not isinstance(
            raw_results,
            dict
        ):
            raise RuntimeError(
                "PexelsService response is missing "
                "'raw_results'."
            )

        if not isinstance(
            filtered_results,
            dict
        ):
            raise RuntimeError(
                "PexelsService response is missing "
                "'filtered_results'."
            )

        # -----------------------------------------------------
        # STEP 4
        # Display Pipeline Results
        # -----------------------------------------------------

        raw_count = raw_results.get(
            "total_results",
            0
        )

        filtered_count = filtered_results.get(
            "total_after_filtering",
            0
        )

        removed_count = filtered_results.get(
            "total_removed",
            0
        )

        print(
            f"[ResearchAgent] "
            f"Retrieved {raw_count} raw images."
        )

        print(
            f"[ResearchAgent] "
            f"After filtering: "
            f"{filtered_count} images remain."
        )

        print(
            f"[ResearchAgent] "
            f"Removed: {removed_count} images."
        )

        # -----------------------------------------------------
        # STEP 5
        # Return Complete Results
        # -----------------------------------------------------

        return {
            "research_plan": research_plan,

            "image_results": {
                "raw_results": raw_results,
                "filtered_results": filtered_results
            }
        }

    # ---------------------------------------------------------
    # GENERATE RESEARCH PLAN
    # ---------------------------------------------------------

    def _generate_research_plan(
        self,
        design_requirements
    ):
        """
        Ask Ollama GPT 120B to convert
        DesignRequirements into a structured
        ResearchPlan.
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

{json.dumps(
    design_requirements,
    indent=4
)}
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

        # -----------------------------------------------------
        # Extract Model Response
        # -----------------------------------------------------

        try:

            content = data[
                "message"
            ][
                "content"
            ]

        except (KeyError, TypeError):

            raise RuntimeError(
                "Unexpected response format from Ollama."
            )

        # -----------------------------------------------------
        # Parse JSON
        # -----------------------------------------------------

        try:

            research_plan = json.loads(
                content
            )

        except json.JSONDecodeError:

            raise RuntimeError(
                "Research Agent returned invalid JSON."
            )

        # -----------------------------------------------------
        # Validate Research Plan
        # -----------------------------------------------------

        self._validate_research_plan(
            research_plan
        )

        return research_plan

    # ---------------------------------------------------------
    # VALIDATE RESEARCH PLAN
    # ---------------------------------------------------------

    def _validate_research_plan(
        self,
        research_plan
    ):
        """
        Make sure the Research Agent returned
        all required ResearchPlan fields.
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

        if not isinstance(
            research_plan,
            dict
        ):

            raise ValueError(
                "Research plan must be a dictionary."
            )

        # -----------------------------------------------------
        # Check Missing Fields
        # -----------------------------------------------------

        missing_fields = [
            field
            for field in required_fields
            if field not in research_plan
        ]

        if missing_fields:

            raise ValueError(
                "Research plan is missing fields: "
                + ", ".join(
                    missing_fields
                )
            )

        # -----------------------------------------------------
        # Check List Fields
        # -----------------------------------------------------

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
                    f"Research plan field "
                    f"'{field}' must be a list."
                )

        # -----------------------------------------------------
        # Check Research Objective
        # -----------------------------------------------------

        if not isinstance(
            research_plan[
                "research_objective"
            ],
            str
        ):

            raise ValueError(
                "research_objective must be a string."
            )

        # -----------------------------------------------------
        # At Least One Search Query
        # -----------------------------------------------------

        if not research_plan[
            "primary_search_queries"
        ]:

            raise ValueError(
                "Research Agent did not generate "
                "any primary search queries."
            )

    # ---------------------------------------------------------
    # OPTIONAL: RESEARCH PLAN ONLY
    # ---------------------------------------------------------

    def generate_research_plan(
        self,
        design_requirements
    ):
        """
        Generate only the ResearchPlan.

        Useful for testing the Research Agent
        without calling PexelsService.
        """

        return self._generate_research_plan(
            design_requirements
        )


# -------------------------------------------------------------
# OPTIONAL DIRECT TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    agent = ResearchAgent()

    test_requirements = {
        "category": "jacket",
        "purpose": "daily wear",
        "audience": "gender-neutral",
        "style": [
            "utility",
            "minimal"
        ],
        "colors": [
            "dark green",
            "cream"
        ],
        "materials": [],
        "silhouette": [
            "oversized"
        ],
        "required_features": [
            "utility pockets"
        ],
        "excluded_features": [
            "visible logos",
            "military styling"
        ],
        "historical_influences": [],
        "functional_requirements": [
            "beginner-friendly construction"
        ],
        "complexity": "beginner",
        "manufacturing_method": None,
        "preferred_direction": None,
        "user_preferences": [
            "gender-neutral",
            "fall season"
        ],
        "special_constraints": [
            "no visible logos",
            "no military styling"
        ],
        "search_terms": [
            "gender neutral oversized fall jacket",
            "dark green cream utility jacket",
            "beginner friendly jacket construction"
        ],
        "confidence": 0.97
    }

    result = agent.research(
        test_requirements
    )

    print(
        "\nRESEARCH AGENT RESULT"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )