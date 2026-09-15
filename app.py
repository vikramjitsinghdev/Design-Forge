import time

from flask import Flask, request, jsonify
from flask_cors import CORS

from agents.input_agent import InputAgent
from agents.research_agent import ResearchAgent


# =============================================================
# FLASK APPLICATION
# =============================================================

app = Flask(__name__)

# Allow the frontend to communicate with Flask
CORS(app)


# =============================================================
# INITIALIZE SERVICES
# =============================================================

try:

    input_agent = InputAgent()
    research_agent = ResearchAgent()

    print("\n[DesignForge] Services initialized successfully.")

except Exception as e:

    print(
        f"\n[DesignForge] Failed to initialize services: {e}"
    )

    input_agent = None
    research_agent = None


# =============================================================
# HEALTH CHECK
# =============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Check whether the DesignForge backend is running.
    """

    return jsonify({
        "status": "ok",
        "service": "DesignForge",
        "agents": {
            "input_agent": input_agent is not None,
            "research_agent": research_agent is not None
        }
    })


# =============================================================
# MAIN DESIGN RESEARCH ENDPOINT
# =============================================================

@app.route("/api/design", methods=["POST"])
def create_design_research():
    """
    Main DesignForge pipeline.

    Expected request:

        {
            "prompt": "I want a gender-neutral fall jacket..."
        }

    Pipeline:

        User Input
             ↓
        InputAgent
             ↓
        DesignRequirements
             ↓
        ResearchAgent
             ↓
        ResearchPlan
             ↓
        PexelsService
             ↓
        FilterService
             ↓
        Final Research Result
    """

    start_time = time.perf_counter()

    # ---------------------------------------------------------
    # Check Services
    # ---------------------------------------------------------

    if input_agent is None or research_agent is None:

        return jsonify({
            "success": False,
            "error": "DesignForge services are not initialized."
        }), 500

    # ---------------------------------------------------------
    # Validate Request
    # ---------------------------------------------------------

    if not request.is_json:

        return jsonify({
            "success": False,
            "error": "Request must contain JSON data."
        }), 400

    data = request.get_json()

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "error": "Request body must be a JSON object."
        }), 400

    user_input = data.get("prompt")

    if not isinstance(user_input, str):

        return jsonify({
            "success": False,
            "error": "The 'prompt' field must be a string."
        }), 400

    user_input = user_input.strip()

    if not user_input:

        return jsonify({
            "success": False,
            "error": "Design prompt cannot be empty."
        }), 400

    # ---------------------------------------------------------
    # STEP 1
    # InputAgent
    # ---------------------------------------------------------

    try:

        print("\n" + "=" * 70)
        print("[DesignForge] NEW DESIGN REQUEST")
        print("=" * 70)

        print(
            f"\n[DesignForge] User request:\n"
            f"{user_input}"
        )

        print(
            "\n[DesignForge] "
            "Step 1: Analyzing user input..."
        )

        input_start = time.perf_counter()

        design_requirements = (
            input_agent.analyze_input(
                user_input
            )
        )

        input_time = (
            time.perf_counter()
            - input_start
        )

        print(
            "[DesignForge] "
            f"Input analysis complete "
            f"({input_time:.2f}s)."
        )

    except Exception as e:

        print(
            f"[DesignForge] "
            f"InputAgent failed: {e}"
        )

        return jsonify({
            "success": False,
            "stage": "input_agent",
            "error": str(e)
        }), 500

    # ---------------------------------------------------------
    # STEP 2
    # ResearchAgent
    # ---------------------------------------------------------

    try:

        print(
            "\n[DesignForge] "
            "Step 2: Creating research plan "
            "and researching references..."
        )

        research_start = time.perf_counter()

        research_result = (
            research_agent.research(
                design_requirements
            )
        )

        research_time = (
            time.perf_counter()
            - research_start
        )

        print(
            "[DesignForge] "
            f"Research pipeline complete "
            f"({research_time:.2f}s)."
        )

    except Exception as e:

        print(
            f"[DesignForge] "
            f"ResearchAgent failed: {e}"
        )

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": str(e)
        }), 500

    # ---------------------------------------------------------
    # STEP 3
    # Validate Research Result
    # ---------------------------------------------------------

    if not isinstance(
        research_result,
        dict
    ):

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": "ResearchAgent returned invalid data."
        }), 500

    research_plan = research_result.get(
        "research_plan"
    )

    image_results = research_result.get(
        "image_results"
    )

    if not isinstance(
        research_plan,
        dict
    ):

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": "ResearchPlan is missing."
        }), 500

    if not isinstance(
        image_results,
        dict
    ):

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": "Image results are missing."
        }), 500

    # ---------------------------------------------------------
    # STEP 4
    # Extract Result Statistics
    # ---------------------------------------------------------

    raw_results = image_results.get(
        "raw_results",
        {}
    )

    filtered_results = image_results.get(
        "filtered_results",
        {}
    )

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

    # ---------------------------------------------------------
    # STEP 5
    # Total Pipeline Time
    # ---------------------------------------------------------

    total_time = (
        time.perf_counter()
        - start_time
    )

    print(
        "\n[DesignForge] "
        "Pipeline completed successfully."
    )

    print(
        f"[DesignForge] "
        f"Raw images: {raw_count}"
    )

    print(
        f"[DesignForge] "
        f"Filtered images: {filtered_count}"
    )

    print(
        f"[DesignForge] "
        f"Removed images: {removed_count}"
    )

    print(
        f"[DesignForge] "
        f"Total time: {total_time:.2f}s"
    )

    # ---------------------------------------------------------
    # STEP 6
    # Return Result to Frontend
    # ---------------------------------------------------------

    return jsonify({

        "success": True,

        "timing": {
            "input_agent_seconds": round(
                input_time,
                2
            ),

            "research_pipeline_seconds": round(
                research_time,
                2
            ),

            "total_seconds": round(
                total_time,
                2
            )
        },

        "design_requirements":
            design_requirements,

        "research_plan":
            research_plan,

        "image_results": {

            "raw_results":
                raw_results,

            "filtered_results":
                filtered_results
        },

        "statistics": {

            "raw_images":
                raw_count,

            "filtered_images":
                filtered_count,

            "removed_images":
                removed_count
        }
    })


# =============================================================
# SIMPLE DEVELOPMENT TEST
# =============================================================

@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """
    Simple endpoint for checking that Flask routes work.
    """

    return jsonify({
        "success": True,
        "message": "DesignForge API is running."
    })


# =============================================================
# ERROR HANDLERS
# =============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "success": False,
        "error": "HTTP method not allowed."
    }), 405


@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("DESIGNFORGE BACKEND")
    print("=" * 70)

    print("\nAvailable endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/test")
    print("  POST /api/design")

    print("\nStarting Flask server...\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )