import re


class FilterService:
    """
    Filter Service for DesignForge.

    Responsibility:
    - Filter obvious image mismatches.
    - Apply hard exclusions from the ResearchPlan.
    - Perform basic metadata/query-based requirement checks.
    - Preserve uncertain images for later ranking/visual analysis.

    This service does NOT:
    - Use AI.
    - Call Pexels.
    - Search the internet.
    - Rank images.
    - Analyze image pixels.
    - Access the database.
    """

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self):
        """
        Initialize the Filter Service.
        """

        pass

    # ---------------------------------------------------------
    # MAIN FILTER METHOD
    # ---------------------------------------------------------

    def filter_images(
        self,
        image_results: dict,
        research_plan: dict
    ) -> dict:
        """
        Filter image references using the ResearchPlan.

        Args:
            image_results:
                Output from PexelsService.

            research_plan:
                Output from ResearchAgent.

        Returns:
            {
                "images": [...],
                "removed_images": [...],
                "total_before_filtering": int,
                "total_after_filtering": int,
                "total_removed": int
            }
        """

        # -----------------------------------------------------
        # VALIDATE INPUTS
        # -----------------------------------------------------

        if not isinstance(image_results, dict):
            raise TypeError(
                "image_results must be a dictionary."
            )

        if not isinstance(research_plan, dict):
            raise TypeError(
                "research_plan must be a dictionary."
            )

        images = image_results.get(
            "images",
            []
        )

        if not isinstance(images, list):
            raise ValueError(
                "image_results['images'] must be a list."
            )

        hard_requirements = research_plan.get(
            "hard_requirements",
            []
        )

        hard_exclusions = research_plan.get(
            "hard_exclusions",
            []
        )

        if not isinstance(hard_requirements, list):
            hard_requirements = []

        if not isinstance(hard_exclusions, list):
            hard_exclusions = []

        # -----------------------------------------------------
        # RESULTS
        # -----------------------------------------------------

        filtered_images = []

        removed_images = []

        # -----------------------------------------------------
        # PROCESS EACH IMAGE
        # -----------------------------------------------------

        for image in images:

            if not isinstance(image, dict):
                continue

            searchable_text = self._build_searchable_text(
                image
            )

            # ---------------------------------------------
            # CHECK HARD EXCLUSIONS
            # ---------------------------------------------

            exclusion = self._find_exclusion_match(
                searchable_text,
                hard_exclusions
            )

            if exclusion:

                removed_images.append({
                    "image": image,
                    "reason": "hard_exclusion",
                    "matched_rule": exclusion
                })

                continue

            # ---------------------------------------------
            # IMAGE PASSES FILTER
            # ---------------------------------------------

            filtered_images.append(
                image
            )

        # -----------------------------------------------------
        # RETURN RESULTS
        # -----------------------------------------------------

        return {
            "images": filtered_images,

            "removed_images": removed_images,

            "total_before_filtering": len(images),

            "total_after_filtering": len(
                filtered_images
            ),

            "total_removed": len(
                removed_images
            )
        }

    # ---------------------------------------------------------
    # BUILD SEARCHABLE TEXT
    # ---------------------------------------------------------

    def _build_searchable_text(
        self,
        image: dict
    ) -> str:
        """
        Combine all useful text metadata from an image.

        Pexels currently gives us information such as:
        - search query
        - photographer
        - Pexels URL
        - image URL

        This does NOT inspect the actual image.
        """

        values = [
            image.get("query", ""),
            image.get("photographer", ""),
            image.get("pexels_url", "")
        ]

        text = " ".join(
            str(value)
            for value in values
            if value
        )

        return text.lower()

    # ---------------------------------------------------------
    # FIND EXCLUSION MATCH
    # ---------------------------------------------------------

    def _find_exclusion_match(
        self,
        text: str,
        exclusions: list
    ):
        """
        Determine whether an image matches a hard exclusion.

        Returns:
            The matched exclusion string,
            or None if there is no match.

        Important:
            This method only removes an image when the
            exclusion can reasonably be detected from
            available metadata/search text.
        """

        for exclusion in exclusions:

            if not isinstance(
                exclusion,
                str
            ):
                continue

            exclusion = exclusion.strip()

            if not exclusion:
                continue

            keywords = self._extract_keywords(
                exclusion
            )

            if not keywords:
                continue

            # ---------------------------------------------
            # ALL meaningful keywords must be present
            # ---------------------------------------------

            if all(
                keyword in text
                for keyword in keywords
            ):

                return exclusion

        return None

    # ---------------------------------------------------------
    # EXTRACT KEYWORDS
    # ---------------------------------------------------------

    def _extract_keywords(
        self,
        phrase: str
    ) -> list:
        """
        Extract meaningful keywords from a requirement.

        Example:

            "visible logos"

        becomes:

            ["visible", "logos"]

        Common filler words are removed.
        """

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "with",
            "without",
            "no",
            "not",
            "very",
            "overly",
            "style",
            "styling",
            "design",
            "construction"
        }

        words = re.findall(
            r"[a-zA-Z]+",
            phrase.lower()
        )

        keywords = [
            word
            for word in words
            if word not in stop_words
            and len(word) > 2
        ]

        return keywords

    # ---------------------------------------------------------
    # REQUIREMENT INFORMATION
    # ---------------------------------------------------------

    def analyze_requirements(
        self,
        image: dict,
        research_plan: dict
    ) -> dict:
        """
        Determine how well an image's search metadata
        represents the ResearchPlan requirements.

        This does NOT remove the image.

        It provides useful information for the future
        RankService.

        Returns:

            {
                "matched_requirements": [...],
                "unmatched_requirements": [...],
                "requirement_score": 0.0
            }
        """

        query = str(
            image.get("query", "")
        ).lower()

        requirements = research_plan.get(
            "hard_requirements",
            []
        )

        if not isinstance(
            requirements,
            list
        ):

            requirements = []

        matched = []

        unmatched = []

        # -----------------------------------------------------
        # CHECK EACH REQUIREMENT
        # -----------------------------------------------------

        for requirement in requirements:

            if not isinstance(
                requirement,
                str
            ):
                continue

            keywords = self._extract_keywords(
                requirement
            )

            if not keywords:
                continue

            # If at least one meaningful keyword is present,
            # record the requirement as represented by the
            # search query.
            if any(
                keyword in query
                for keyword in keywords
            ):

                matched.append(
                    requirement
                )

            else:

                unmatched.append(
                    requirement
                )

        # -----------------------------------------------------
        # CALCULATE BASIC SCORE
        # -----------------------------------------------------

        total_requirements = (
            len(matched)
            + len(unmatched)
        )

        if total_requirements > 0:

            score = (
                len(matched)
                / total_requirements
            )

        else:

            score = 0.0

        return {
            "matched_requirements": matched,

            "unmatched_requirements": unmatched,

            "requirement_score": round(
                score,
                3
            )
        }

    # ---------------------------------------------------------
    # PREPARE IMAGES FOR RANKING
    # ---------------------------------------------------------

    def prepare_for_ranking(
        self,
        image_results: dict,
        research_plan: dict
    ) -> list:
        """
        Prepare filtered images with basic requirement
        information.

        This does NOT rank the images.

        It simply attaches requirement-analysis data
        that RankService can use later.
        """

        images = image_results.get(
            "images",
            []
        )

        prepared_images = []

        for image in images:

            requirement_analysis = (
                self.analyze_requirements(
                    image,
                    research_plan
                )
            )

            prepared_image = {
                **image,

                "filter_analysis": {
                    "matched_requirements":
                        requirement_analysis[
                            "matched_requirements"
                        ],

                    "unmatched_requirements":
                        requirement_analysis[
                            "unmatched_requirements"
                        ],

                    "requirement_score":
                        requirement_analysis[
                            "requirement_score"
                        ]
                }
            }

            prepared_images.append(
                prepared_image
            )

        return prepared_images