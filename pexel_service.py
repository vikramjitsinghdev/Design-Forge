import os
import requests
from dotenv import load_dotenv


load_dotenv()


class PexelsService:
    """
    Handles all communication with the Pexels API.

    Input:
        ResearchPlan dictionary containing:
            - primary_search_queries
            - alternative_search_queries

    Output:
        Standardized list of image reference dictionaries.
    """

    BASE_URL = "https://api.pexels.com/v1/search"

    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("PEXELS_API_KEY")

        if not self.api_key:
            raise ValueError(
                "PEXELS_API_KEY not found. "
                "Make sure your .env file contains: "
                "PEXELS_API_KEY=your_key"
            )

        self.headers = {
            "Authorization": self.api_key
        }
    # ---------------------------------------------------------
    # SEARCH ONE QUERY
    # ---------------------------------------------------------

    def search_images(self, query, per_page=5):
        """
        Search Pexels using one search query.

        Returns:
            List of standardized image dictionaries.
        """

        if not query or not isinstance(query, str):
            return []

        params = {
            "query": query,
            "per_page": per_page
        }

        try:
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            return self._format_results(data.get("photos", []), query)

        except requests.exceptions.RequestException as e:
            print(f"Pexels API error for '{query}': {e}")
            return []

    # ---------------------------------------------------------
    # SEARCH RESEARCH PLAN
    # ---------------------------------------------------------

    def search_research_plan(
        self,
        research_plan,
        primary_per_query=4,
        alternative_per_query=2,
        max_results=20
    ):
        """
        Directly accepts the output of ResearchAgent.

        Expected structure:

        {
            "primary_search_queries": [...],
            "alternative_search_queries": [...]
        }

        Primary queries are searched first.
        Alternative queries are used to expand the results.

        Returns:
            {
                "images": [...],
                "queries_used": [...],
                "total_results": int
            }
        """

        if not isinstance(research_plan, dict):
            raise TypeError("research_plan must be a dictionary")

        primary_queries = research_plan.get(
            "primary_search_queries",
            []
        )

        alternative_queries = research_plan.get(
            "alternative_search_queries",
            []
        )

        if not isinstance(primary_queries, list):
            primary_queries = []

        if not isinstance(alternative_queries, list):
            alternative_queries = []

        results = []
        queries_used = []

        # -----------------------------------------------------
        # PRIMARY QUERIES
        # -----------------------------------------------------

        for query in primary_queries:

            if len(results) >= max_results:
                break

            images = self.search_images(
                query=query,
                per_page=primary_per_query
            )

            results.extend(images)
            queries_used.append(query)

        # -----------------------------------------------------
        # ALTERNATIVE QUERIES
        # -----------------------------------------------------

        for query in alternative_queries:

            if len(results) >= max_results:
                break

            images = self.search_images(
                query=query,
                per_page=alternative_per_query
            )

            results.extend(images)
            queries_used.append(query)

        # -----------------------------------------------------
        # REMOVE DUPLICATES
        # -----------------------------------------------------

        results = self._remove_duplicates(results)

        # Limit final result count
        results = results[:max_results]

        return {
            "images": results,
            "queries_used": queries_used,
            "total_results": len(results)
        }

    # ---------------------------------------------------------
    # FORMAT PEXELS RESULTS
    # ---------------------------------------------------------

    def _format_results(self, photos, query):
        """
        Convert raw Pexels API responses into a consistent
        structure that the rest of DesignLens can use.
        """

        formatted = []

        for photo in photos:

            formatted.append({
                "id": photo.get("id"),

                "source": "pexels",

                "query": query,

                "image_url": photo.get("src", {}).get("large"),

                "original_url": photo.get("src", {}).get("original"),

                "thumbnail_url": photo.get("src", {}).get("medium"),

                "width": photo.get("width"),

                "height": photo.get("height"),

                "photographer": photo.get("photographer"),

                "photographer_url": photo.get("photographer_url"),

                "pexels_url": photo.get("url")
            })

        return formatted

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    def _remove_duplicates(self, images):
        """
        Remove duplicate Pexels images using their Pexels ID.
        """

        unique_images = []
        seen_ids = set()

        for image in images:

            image_id = image.get("id")

            if image_id is None:
                continue

            if image_id not in seen_ids:

                seen_ids.add(image_id)
                unique_images.append(image)

        return unique_images