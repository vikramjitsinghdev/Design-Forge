import json
import time

from agents.input_agent import InputAgent
from agents.research_agent import ResearchAgent


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():

    # =========================================================
    # TEST INPUT
    # =========================================================

    user_prompt = """
    I want a gender-neutral fall jacket for daily wear.
    It should have an oversized silhouette and a modern,
    minimalist utility style.

    I want dark green and cream colours with large functional
    pockets. The construction should be simple and
    beginner-friendly.

    Avoid visible logos, military styling, and overly
    complicated construction.
    """

    print_section("DESIGNFORGE FULL PIPELINE TEST")

    print("\nUser Request:")
    print(user_prompt.strip())

    total_start = time.time()

    # =========================================================
    # 1. INPUT AGENT
    # =========================================================

    print_section("[1] INPUT AGENT - GROQ")

    input_start = time.time()

    try:
        input_agent = InputAgent()

        requirements = input_agent.analyze_input(
            user_prompt
        )

        input_time = time.time() - input_start

        print("✓ Input Agent completed")
        print(f"Time: {input_time:.2f} seconds")

    except Exception as e:

        print("✗ Input Agent failed")
        print(f"Error: {e}")

        return

    # =========================================================
    # DISPLAY DESIGN REQUIREMENTS
    # =========================================================

    print("\nStructured Design Requirements:")

    print(
        json.dumps(
            requirements,
            indent=4,
            ensure_ascii=False
        )
    )

    # =========================================================
    # 2. RESEARCH AGENT
    # =========================================================

    print_section("[2] RESEARCH AGENT - OLLAMA")

    research_start = time.time()

    try:
        research_agent = ResearchAgent()

        # IMPORTANT:
        # research() automatically:
        #
        # DesignRequirements
        #       ↓
        # Ollama
        #       ↓
        # ResearchPlan
        #       ↓
        # PexelsService
        #       ↓
        # Image Results

        result = research_agent.research(
            requirements
        )

        research_time = time.time() - research_start

        print("✓ Research Agent completed")
        print(f"Time: {research_time:.2f} seconds")

    except Exception as e:

        print("✗ Research Agent failed")
        print(f"Error: {e}")

        return

    # =========================================================
    # 3. RESEARCH PLAN
    # =========================================================

    research_plan = result.get(
        "research_plan"
    )

    if not research_plan:

        print("\n✗ Research Plan is missing")
        return

    print_section("[3] GENERATED RESEARCH PLAN")

    print(
        json.dumps(
            research_plan,
            indent=4,
            ensure_ascii=False
        )
    )

    # =========================================================
    # 4. VERIFY SEARCH QUERIES
    # =========================================================

    print_section("[4] SEARCH QUERIES SENT TO PEXELS")

    primary_queries = research_plan.get(
        "primary_search_queries",
        []
    )

    alternative_queries = research_plan.get(
        "alternative_search_queries",
        []
    )

    print("\nPrimary Queries:")

    for i, query in enumerate(
        primary_queries,
        start=1
    ):
        print(f"  {i}. {query}")

    print("\nAlternative Queries:")

    for i, query in enumerate(
        alternative_queries,
        start=1
    ):
        print(f"  {i}. {query}")

    # =========================================================
    # 5. PEXELS RESULTS
    # =========================================================

    image_results = result.get(
        "image_results"
    )

    if not image_results:

        print("\n✗ Pexels results are missing")
        return

    print_section("[5] PEXELS IMAGE RESULTS")

    total_images = image_results.get(
        "total_results",
        0
    )

    queries_used = image_results.get(
        "queries_used",
        []
    )

    images = image_results.get(
        "images",
        []
    )

    print(f"\nTotal Images: {total_images}")

    print("\nQueries Actually Used:")

    for query in queries_used:
        print(f"  - {query}")

    # =========================================================
    # 6. DISPLAY IMAGES
    # =========================================================

    print("\nImage References:")

    for index, image in enumerate(
        images,
        start=1
    ):

        print("\n-----------------------------")

        print(f"Image #{index}")

        print(f"ID: {image.get('id')}")

        print(
            f"Query: {image.get('query')}"
        )

        print(
            f"Photographer: "
            f"{image.get('photographer')}"
        )

        print(
            f"Image URL: "
            f"{image.get('image_url')}"
        )

        print(
            f"Thumbnail URL: "
            f"{image.get('thumbnail_url')}"
        )

        print(
            f"Pexels URL: "
            f"{image.get('pexels_url')}"
        )

    # =========================================================
    # 7. VALIDATION
    # =========================================================

    print_section("[6] PIPELINE VALIDATION")

    tests_passed = 0
    tests_failed = 0

    # ---------------------------------------------------------
    # Test 1
    # ---------------------------------------------------------

    if isinstance(requirements, dict):

        print("✓ Input Agent returned dictionary")

        tests_passed += 1

    else:

        print("✗ Input Agent did not return dictionary")

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 2
    # ---------------------------------------------------------

    required_input_fields = [
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

    missing_input_fields = [
        field
        for field in required_input_fields
        if field not in requirements
    ]

    if not missing_input_fields:

        print("✓ Input Agent schema is valid")

        tests_passed += 1

    else:

        print(
            "✗ Input Agent missing fields:",
            missing_input_fields
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 3
    # ---------------------------------------------------------

    if isinstance(research_plan, dict):

        print("✓ Research Agent returned dictionary")

        tests_passed += 1

    else:

        print(
            "✗ Research Agent did not return dictionary"
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 4
    # ---------------------------------------------------------

    required_research_fields = [
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

    missing_research_fields = [
        field
        for field in required_research_fields
        if field not in research_plan
    ]

    if not missing_research_fields:

        print("✓ Research Agent schema is valid")

        tests_passed += 1

    else:

        print(
            "✗ Research Agent missing fields:",
            missing_research_fields
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 5
    # ---------------------------------------------------------

    if primary_queries:

        print(
            "✓ Research Agent generated search queries"
        )

        tests_passed += 1

    else:

        print(
            "✗ No primary search queries generated"
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 6
    # ---------------------------------------------------------

    if isinstance(image_results, dict):

        print(
            "✓ Pexels returned structured results"
        )

        tests_passed += 1

    else:

        print(
            "✗ Pexels results are not a dictionary"
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 7
    # ---------------------------------------------------------

    if images:

        print(
            f"✓ Pexels returned {len(images)} images"
        )

        tests_passed += 1

    else:

        print(
            "✗ Pexels returned no images"
        )

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 8
    # ---------------------------------------------------------

    required_image_fields = [
        "id",
        "source",
        "query",
        "image_url",
        "thumbnail_url",
        "photographer",
        "pexels_url"
    ]

    invalid_images = []

    for image in images:

        missing_fields = [
            field
            for field in required_image_fields
            if field not in image
        ]

        if missing_fields:

            invalid_images.append({
                "id": image.get("id"),
                "missing": missing_fields
            })

    if not invalid_images:

        print(
            "✓ Pexels image structure is valid"
        )

        tests_passed += 1

    else:

        print(
            "✗ Some images have missing fields:"
        )

        for invalid in invalid_images:
            print(invalid)

        tests_failed += 1

    # ---------------------------------------------------------
    # Test 9
    # ---------------------------------------------------------

    pexels_sources = [
        image.get("source")
        for image in images
    ]

    if all(
        source == "pexels"
        for source in pexels_sources
    ):

        print(
            "✓ All image references identify Pexels"
        )

        tests_passed += 1

    else:

        print(
            "✗ Some image references have "
            "incorrect source"
        )

        tests_failed += 1

    # =========================================================
    # FINAL RESULT
    # =========================================================

    total_time = time.time() - total_start

    print_section("FINAL TEST RESULT")

    print(
        f"Tests Passed: {tests_passed}"
    )

    print(
        f"Tests Failed: {tests_failed}"
    )

    print(
        f"Total Pipeline Time: "
        f"{total_time:.2f} seconds"
    )

    print("\nPipeline:")

    print(
        "User Input"
        " → Groq InputAgent"
        " → DesignRequirements"
        " → Ollama ResearchAgent"
        " → ResearchPlan"
        " → PexelsService"
        " → Image References"
    )

    if tests_failed == 0:

        print("\n" + "=" * 60)
        print("✓ COMPLETE DESIGNFORGE PIPELINE PASSED")
        print("=" * 60)

    else:

        print("\n" + "=" * 60)
        print("✗ PIPELINE HAS FAILURES")
        print("=" * 60)


if __name__ == "__main__":
    main()