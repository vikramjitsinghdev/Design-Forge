import json
from agents.input_agent import InputAgent


def main():
    # ---------------------------------------------------------
    # TEST USER PROMPT
    # ---------------------------------------------------------

    user_prompt = """
    I want to design a gender-neutral fall jacket.
    I want it to have an oversized silhouette with a
    modern minimalist utility style.

    The main colours should be dark green and cream.
    I want large functional pockets and a simple construction
    that a beginner could realistically make.

    I don't want any visible logos, military styling, or
    overly complicated construction.

    The jacket should be practical for everyday use but still
    look fashionable and clean.
    """

    print("=" * 70)
    print("DESIGNLENS - INPUT AGENT TEST")
    print("=" * 70)

    print("\nUSER INPUT:")
    print("-" * 70)
    print(user_prompt.strip())

    # ---------------------------------------------------------
    # CREATE INPUT AGENT
    # ---------------------------------------------------------

    try:
        input_agent = InputAgent()

    except Exception as e:
        print("\nERROR INITIALIZING INPUT AGENT")
        print("-" * 70)
        print(e)
        return

    # ---------------------------------------------------------
    # SEND USER INPUT TO INPUT AGENT
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("SENDING INPUT TO GROQ...")
    print("=" * 70)

    try:
        requirements = input_agent.analyze_input(user_prompt)

    except Exception as e:
        print("\nERROR FROM INPUT AGENT")
        print("-" * 70)
        print(e)
        return

    # ---------------------------------------------------------
    # DISPLAY RESULT
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("INPUT AGENT OUTPUT")
    print("=" * 70)

    print(json.dumps(requirements, indent=4))

    # ---------------------------------------------------------
    # DISPLAY IMPORTANT FIELDS SEPARATELY
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("INTERPRETED DESIGN REQUIREMENTS")
    print("=" * 70)

    print(f"\nCategory:")
    print(f"  {requirements['category']}")

    print(f"\nPurpose:")
    print(f"  {requirements['purpose']}")

    print(f"\nAudience:")
    print(f"  {requirements['audience']}")

    print(f"\nStyle:")
    print(f"  {', '.join(requirements['style'])}")

    print(f"\nColours:")
    print(f"  {', '.join(requirements['colors'])}")

    print(f"\nMaterials:")
    print(f"  {', '.join(requirements['materials'])}")

    print(f"\nSilhouette:")
    print(f"  {', '.join(requirements['silhouette'])}")

    print(f"\nRequired Features:")
    print(f"  {', '.join(requirements['required_features'])}")

    print(f"\nExcluded Features:")
    print(f"  {', '.join(requirements['excluded_features'])}")

    print(f"\nFunctional Requirements:")
    print(f"  {', '.join(requirements['functional_requirements'])}")

    print(f"\nComplexity:")
    print(f"  {requirements['complexity']}")

    print(f"\nManufacturing Method:")
    print(f"  {requirements['manufacturing_method']}")

    print(f"\nPreferred Direction:")
    print(f"  {requirements['preferred_direction']}")

    print(f"\nSpecial Constraints:")
    print(f"  {', '.join(requirements['special_constraints'])}")

    print(f"\nSearch Terms:")
    print(f"  {', '.join(requirements['search_terms'])}")

    print(f"\nConfidence:")
    print(f"  {requirements['confidence']}")

    print("\n")
    print("=" * 70)
    print("INPUT AGENT TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()