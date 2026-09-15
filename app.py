import time
import threading
import webbrowser

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from agents.input_agent import InputAgent
from agents.research_agent import ResearchAgent


# =============================================================
# DESIGNFORGE APPLICATION
# =============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Allow frontend requests to communicate with the Flask API.
CORS(app)


# =============================================================
# APPLICATION CONFIGURATION
# =============================================================

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


# =============================================================
# INITIALIZE SERVICES
# =============================================================

input_agent = None
research_agent = None

services_initialized = False
initialization_error = None


def initialize_services():
    """
    Initialize the DesignForge AI services.

    Architecture:

        Frontend
            ↓
        Flask
            ↓
        InputAgent
            ↓
        DesignRequirements
            ↓
        ResearchAgent
            ↓
        ResearchPlan
            ↓
        Pexels / Filtering
            ↓
        Final JSON
            ↓
        Frontend
    """

    global input_agent
    global research_agent
    global services_initialized
    global initialization_error

    print()
    print("=" * 70)
    print("DESIGNFORGE SERVICE INITIALIZATION")
    print("=" * 70)

    try:

        print()
        print("[DesignForge] Initializing InputAgent...")

        input_agent = InputAgent()

        print(
            "[DesignForge] InputAgent initialized successfully."
        )

        print()
        print("[DesignForge] Initializing ResearchAgent...")

        research_agent = ResearchAgent()

        print(
            "[DesignForge] ResearchAgent initialized successfully."
        )

        services_initialized = True
        initialization_error = None

        print()
        print(
            "[DesignForge] Services initialized successfully."
        )

    except Exception as e:

        input_agent = None
        research_agent = None

        services_initialized = False
        initialization_error = str(e)

        print()
        print(
            "[DesignForge] Service initialization failed."
        )

        print(
            f"[DesignForge] Error: {e}"
        )


# Initialize the AI services when app.py starts.
initialize_services()


# =============================================================
# FRONTEND ROUTE
# =============================================================

@app.route("/", methods=["GET"])
def home():
    """
    Render the DesignForge frontend.

    Flask looks for:

        templates/index.html
    """

    return render_template("index.html")


# =============================================================
# HEALTH CHECK
# =============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Check whether DesignForge is operational.
    """

    if services_initialized:

        return jsonify({
            "status": "ok",
            "service": "DesignForge",

            "agents": {
                "input_agent": input_agent is not None,
                "research_agent": research_agent is not None
            }
        })

    return jsonify({
        "status": "degraded",
        "service": "DesignForge",

        "agents": {
            "input_agent": input_agent is not None,
            "research_agent": research_agent is not None
        },

        "error": initialization_error
    }), 503


# =============================================================
# API TEST
# =============================================================

@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """
    Simple API connectivity test.
    """

    return jsonify({
        "success": True,
        "message": "DesignForge API is running."
    })


# =============================================================
# MAIN DESIGN PIPELINE
# =============================================================

@app.route("/api/design", methods=["POST"])
def create_design_research():
    """
    Main DesignForge design research pipeline.

    Expected request:

        {
            "prompt": "I want a gender-neutral fall jacket..."
        }

    Pipeline:

        User
          ↓
        index.html
          ↓
        script.js
          ↓
        POST /api/design
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
        JSON response
          ↓
        script.js
          ↓
        DesignForge UI
    """

    start_time = time.perf_counter()

    print()
    print("=" * 70)
    print("[DesignForge] NEW DESIGN REQUEST")
    print("=" * 70)

    # =========================================================
    # CHECK SERVICES
    # =========================================================

    if input_agent is None or research_agent is None:

        print(
            "[DesignForge] Services are not initialized."
        )

        return jsonify({
            "success": False,
            "stage": "initialization",
            "error": (
                "DesignForge services are not initialized."
            )
        }), 500

    # =========================================================
    # VALIDATE REQUEST CONTENT TYPE
    # =========================================================

    if not request.is_json:

        print(
            "[DesignForge] Request rejected: "
            "JSON body required."
        )

        return jsonify({
            "success": False,
            "stage": "request_validation",
            "error": (
                "Request must contain JSON data."
            )
        }), 400

    # =========================================================
    # READ JSON
    # =========================================================

    try:

        data = request.get_json()

    except Exception as e:

        print(
            f"[DesignForge] Invalid JSON: {e}"
        )

        return jsonify({
            "success": False,
            "stage": "request_validation",
            "error": "Invalid JSON request body."
        }), 400

    # =========================================================
    # VALIDATE JSON OBJECT
    # =========================================================

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "stage": "request_validation",
            "error": (
                "Request body must be a JSON object."
            )
        }), 400

    # =========================================================
    # GET USER PROMPT
    # =========================================================

    user_input = data.get("prompt")

    if not isinstance(user_input, str):

        return jsonify({
            "success": False,
            "stage": "request_validation",
            "error": (
                "The 'prompt' field must be a string."
            )
        }), 400

    user_input = user_input.strip()

    if not user_input:

        return jsonify({
            "success": False,
            "stage": "request_validation",
            "error": (
                "Design prompt cannot be empty."
            )
        }), 400

    # =========================================================
    # LOG USER REQUEST
    # =========================================================

    print()
    print("[DesignForge] User request:")
    print(user_input)

    # =========================================================
    # STEP 1 — INPUT AGENT
    # =========================================================

    print()
    print(
        "[DesignForge] Step 1: "
        "Analyzing user input..."
    )

    input_start = time.perf_counter()

    try:

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
            "[DesignForge] Input analysis complete "
            f"({input_time:.2f}s)."
        )

    except Exception as e:

        input_time = (
            time.perf_counter()
            - input_start
        )

        total_time = (
            time.perf_counter()
            - start_time
        )

        print()
        print(
            "[DesignForge] InputAgent failed:"
        )

        print(
            f"[DesignForge] {e}"
        )

        return jsonify({
            "success": False,
            "stage": "input_agent",
            "error": str(e),

            "timing": {
                "input_agent_seconds": round(
                    input_time,
                    2
                ),

                "total_seconds": round(
                    total_time,
                    2
                )
            }
        }), 500

    # =========================================================
    # VALIDATE INPUT AGENT RESULT
    # =========================================================

    if not isinstance(
        design_requirements,
        dict
    ):

        print(
            "[DesignForge] InputAgent returned "
            "invalid data."
        )

        return jsonify({
            "success": False,
            "stage": "input_agent",
            "error": (
                "InputAgent returned invalid data."
            )
        }), 500

    # =========================================================
    # STEP 2 — RESEARCH AGENT
    # =========================================================

    print()
    print(
        "[DesignForge] Step 2: "
        "Creating research plan "
        "and researching references..."
    )

    research_start = time.perf_counter()

    try:

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
            "[DesignForge] Research pipeline "
            f"complete ({research_time:.2f}s)."
        )

    except Exception as e:

        research_time = (
            time.perf_counter()
            - research_start
        )

        total_time = (
            time.perf_counter()
            - start_time
        )

        print()
        print(
            "[DesignForge] ResearchAgent failed:"
        )

        print(
            f"[DesignForge] {e}"
        )

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": str(e),

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
            }
        }), 500

    # =========================================================
    # VALIDATE RESEARCH RESULT
    # =========================================================

    if not isinstance(
        research_result,
        dict
    ):

        print(
            "[DesignForge] ResearchAgent returned "
            "invalid data."
        )

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": (
                "ResearchAgent returned invalid data."
            )
        }), 500

    # =========================================================
    # GET RESEARCH PLAN
    # =========================================================

    research_plan = (
        research_result.get(
            "research_plan"
        )
    )

    if not isinstance(
        research_plan,
        dict
    ):

        print(
            "[DesignForge] ResearchPlan is missing."
        )

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": (
                "ResearchPlan is missing."
            )
        }), 500

    # =========================================================
    # GET IMAGE RESULTS
    # =========================================================

    image_results = (
        research_result.get(
            "image_results"
        )
    )

    if not isinstance(
        image_results,
        dict
    ):

        print(
            "[DesignForge] Image results are missing."
        )

        return jsonify({
            "success": False,
            "stage": "research_agent",
            "error": (
                "Image results are missing."
            )
        }), 500

    # =========================================================
    # EXTRACT RAW RESULTS
    # =========================================================

    raw_results = (
        image_results.get(
            "raw_results",
            {}
        )
    )

    if not isinstance(
        raw_results,
        dict
    ):

        raw_results = {}

    # =========================================================
    # EXTRACT FILTERED RESULTS
    # =========================================================

    filtered_results = (
        image_results.get(
            "filtered_results",
            {}
        )
    )

    if not isinstance(
        filtered_results,
        dict
    ):

        filtered_results = {}

    # =========================================================
    # STATISTICS
    # =========================================================

    raw_count = (
        raw_results.get(
            "total_results",
            0
        )
    )

    filtered_count = (
        filtered_results.get(
            "total_after_filtering",
            0
        )
    )

    removed_count = (
        filtered_results.get(
            "total_removed",
            0
        )
    )

    # Keep statistics JSON-safe.
    if not isinstance(
        raw_count,
        (int, float)
    ):

        raw_count = 0

    if not isinstance(
        filtered_count,
        (int, float)
    ):

        filtered_count = 0

    if not isinstance(
        removed_count,
        (int, float)
    ):

        removed_count = 0

    # =========================================================
    # TOTAL PIPELINE TIME
    # =========================================================

    total_time = (
        time.perf_counter()
        - start_time
    )

    # =========================================================
    # LOG RESULTS
    # =========================================================

    print()
    print("=" * 70)

    print(
        "[DesignForge] "
        "Pipeline completed successfully."
    )

    print(
        f"[DesignForge] Raw images: "
        f"{raw_count}"
    )

    print(
        f"[DesignForge] Filtered images: "
        f"{filtered_count}"
    )

    print(
        f"[DesignForge] Removed images: "
        f"{removed_count}"
    )

    print(
        f"[DesignForge] Input Agent: "
        f"{input_time:.2f}s"
    )

    print(
        f"[DesignForge] Research Pipeline: "
        f"{research_time:.2f}s"
    )

    print(
        f"[DesignForge] TOTAL: "
        f"{total_time:.2f}s"
    )

    print("=" * 70)

    # =========================================================
    # FINAL RESPONSE
    # =========================================================

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
                int(raw_count),

            "filtered_images":
                int(filtered_count),

            "removed_images":
                int(removed_count)
        }
    })


# =============================================================
# 404 HANDLER
# =============================================================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "success": False,
            "error": "API endpoint not found.",
            "path": request.path
        }), 404

    # If someone accesses an unknown normal browser
    # route, return the DesignForge frontend.
    return render_template(
        "index.html"
    )


# =============================================================
# 405 HANDLER
# =============================================================

@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "success": False,
        "error": "HTTP method not allowed.",
        "path": request.path
    }), 405


# =============================================================
# 413 HANDLER
# =============================================================

@app.errorhandler(413)
def request_too_large(error):

    return jsonify({
        "success": False,
        "error": "Request body is too large."
    }), 413


# =============================================================
# 500 HANDLER
# =============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print()
    print(
        f"[DesignForge] Internal server error: {error}"
    )

    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# =============================================================
# AUTOMATIC BROWSER LAUNCH
# =============================================================

def open_browser():
    """
    Open the DesignForge frontend automatically
    after Flask has started.
    """

    webbrowser.open(
        "http://127.0.0.1:5000/"
    )


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("DESIGNFORGE")
    print("=" * 70)

    print()
    print("FRONTEND")
    print("  http://127.0.0.1:5000/")

    print()
    print("API ENDPOINTS")
    print("  GET  /api/health")
    print("  GET  /api/test")
    print("  POST /api/design")

    print()
    print("SERVICES")

    print(
        f"  Input Agent: "
        f"{'READY' if input_agent else 'FAILED'}"
    )

    print(
        f"  Research Agent: "
        f"{'READY' if research_agent else 'FAILED'}"
    )

    if initialization_error:

        print()
        print("INITIALIZATION ERROR")
        print(
            f"  {initialization_error}"
        )

    print()
    print("Starting DesignForge...")
    print("=" * 70)
    print()

    # Open the browser shortly after Flask starts.
    # The small delay prevents the browser from trying to
    # connect before the Flask development server is ready.
    threading.Timer(
        1.0,
        open_browser
    ).start()

    # IMPORTANT:
    # use_reloader=False prevents Flask from launching the
    # application a second time and initializing your AI
    # services twice.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )