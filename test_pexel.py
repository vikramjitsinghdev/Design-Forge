from pexel_service import PexelsService


research_plan = {
    "primary_search_queries": [
        "oversized minimalist utility jacket dark green",
        "gender neutral large pocket jacket cream"
    ],

    "alternative_search_queries": [
        "neutral color utility jacket oversized"
    ]
}


def main():

    print("=" * 60)
    print("PEXELS SERVICE TEST")
    print("=" * 60)

    pexels = PexelsService()

    results = pexels.search_research_plan(
        research_plan,
        primary_per_query=4,
        alternative_per_query=2,
        max_results=10
    )

    print("\nQueries used:")
    for query in results["queries_used"]:
        print(f"  - {query}")

    print(f"\nTotal images: {results['total_results']}")

    print("\nImages:")

    for image in results["images"]:

        print("\n-----------------------------")

        print(f"ID: {image['id']}")
        print(f"Query: {image['query']}")
        print(f"Photographer: {image['photographer']}")
        print(f"Image: {image['image_url']}")
        print(f"Pexels: {image['pexels_url']}")

    print("\n" + "=" * 60)
    print("✓ PEXELS SERVICE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()