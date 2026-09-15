# ============================================================
# IMPORTS
# ============================================================

import os
import time
import json

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    session
)

from flask_cors import CORS
from dotenv import load_dotenv


# DesignForge modules
import database
import user_database
import user_credential

from agents.input_agent import InputAgent
from agents.research_agent import ResearchAgent


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# Secret key is required for Flask sessions.
app.secret_key = os.getenv(
    "DESIGNFORGE_SECRET_KEY",
    "designforge-development-secret-change-this"
)


# Allow frontend API requests.
CORS(app)


# ============================================================
# INITIALIZE DATABASES
# ============================================================

# user_database.py owns:
#     user_database.db
#
# database.py owns:
#     database.db
#
# They are intentionally separate databases.

user_database.initialize_database()
database.initialize_database()


# ============================================================
# INITIALIZE AI AGENTS
# ============================================================

print()
print("=" * 70)
print("DESIGNFORGE BACKEND")
print("=" * 70)

try:

    input_agent = InputAgent()
    research_agent = ResearchAgent()

    print()
    print("✓ InputAgent initialized")
    print("✓ ResearchAgent initialized")

    AGENTS_INITIALIZED = True

except Exception as error:

    print()
    print("✗ Failed to initialize AI agents")
    print(f"  Error: {error}")

    input_agent = None
    research_agent = None

    AGENTS_INITIALIZED = False


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def index():
    """
    Render the main DesignForge frontend.
    """

    return render_template(
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():
    """
    Backend health/status endpoint.
    """

    return jsonify({
        "service": "DesignForge",
        "status": "online",

        "agents": {
            "input_agent":
                input_agent is not None,

            "research_agent":
                research_agent is not None
        },

        "databases": {
            "user_database":
                user_database.database_exists(),

            "design_database":
                database.database_exists()
        }
    })


# ============================================================
# SESSION / CURRENT USER
# ============================================================

@app.route(
    "/api/session",
    methods=["GET"]
)
def get_session():
    """
    Return the currently logged-in user.
    """

    user_id = session.get(
        "user_id"
    )

    if user_id is None:

        return jsonify({
            "authenticated": False,
            "user": None
        })

    user = user_database.get_user(
        user_id
    )

    if user is None:

        session.clear()

        return jsonify({
            "authenticated": False,
            "user": None
        })

    user.pop(
        "password_hash",
        None
    )

    return jsonify({
        "authenticated": True,
        "user": user
    })


# ============================================================
# SIGNUP
# ============================================================

@app.route(
    "/api/signup",
    methods=["POST"]
)
def signup():
    """
    Create a new DesignForge account.
    """

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message":
                "No signup information was provided."
        }), 400

    name = data.get(
        "name",
        ""
    )

    username = data.get(
        "username",
        ""
    )

    password = data.get(
        "password",
        ""
    )

    result = user_credential.signup(
        name=name,
        username=username,
        password=password
    )

    if not result["success"]:

        return jsonify(
            result
        ), 400

    session.clear()

    session["user_id"] = (
        result["user_id"]
    )

    return jsonify({
        "success": True,
        "user_id":
            result["user_id"],
        "message":
            "Account created successfully.",
        "authenticated":
            True
    })


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():
    """
    Authenticate an existing DesignForge user.
    """

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message":
                "Username and password are required."
        }), 400

    username = data.get(
        "username",
        ""
    )

    password = data.get(
        "password",
        ""
    )

    result = user_credential.login(
        username=username,
        password=password
    )

    if not result["success"]:

        return jsonify(
            result
        ), 401

    session.clear()

    session["user_id"] = (
        result["user_id"]
    )

    return jsonify({
        "success": True,
        "user_id":
            result["user_id"],
        "message":
            "Login successful.",
        "authenticated":
            True
    })


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/api/logout",
    methods=["POST"]
)
def logout():
    """
    Log the current user out.
    """

    session.clear()

    return jsonify({
        "success": True,
        "message":
            "Logged out successfully.",
        "authenticated":
            False
    })


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def get_authenticated_user():
    """
    Retrieve the currently authenticated user.

    Returns:
        user dictionary
        or None if the user is not logged in.
    """

    user_id = session.get(
        "user_id"
    )

    if user_id is None:
        return None

    return user_database.get_user(
        user_id
    )


# ============================================================
# DESIGN REQUEST
# ============================================================

@app.route(
    "/api/design",
    methods=["POST"]
)
def process_design():
    """
    Run the complete DesignForge AI pipeline.

    Pipeline:

        User Description
              |
              v
        InputAgent / Groq
              |
              v
        DesignRequirements
              |
              v
        ResearchAgent / Ollama
              |
              v
        ResearchPlan
              |
              v
        PexelsService
              |
              v
        Filtered Image References
              |
              v
        database.py
              |
              v
        Response
    """

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    user = get_authenticated_user()

    if user is None:

        return jsonify({
            "success": False,
            "message":
                "You must be logged in to use DesignForge.",
            "authenticated":
                False
        }), 401

    # ========================================================
    # REQUEST DATA
    # ========================================================

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message":
                "No design request was provided."
        }), 400

    # Support both the current frontend "description"
    # and the older "prompt" field.
    user_description = data.get(
        "description"
    )

    if user_description is None:
        user_description = data.get(
            "prompt",
            ""
        )

    if not isinstance(
        user_description,
        str
    ):

        return jsonify({
            "success": False,
            "message":
                "Design description must be text."
        }), 400

    user_description = (
        user_description.strip()
    )

    if not user_description:

        return jsonify({
            "success": False,
            "message":
                "Please describe the design you want."
        }), 400

    # ========================================================
    # CHECK AGENTS
    # ========================================================

    if not AGENTS_INITIALIZED:

        return jsonify({
            "success": False,
            "message":
                "DesignForge AI services are not available."
        }), 503

    # ========================================================
    # PIPELINE START
    # ========================================================

    pipeline_start = time.perf_counter()

    print()
    print("=" * 70)
    print("DESIGNFORGE REQUEST")
    print("=" * 70)

    print()
    print("USER:")
    print(
        f"  {user['username']}"
    )

    print()
    print("REQUEST:")
    print(
        f"  {user_description}"
    )

    try:

        # ====================================================
        # STEP 1 — INPUT AGENT
        # ====================================================

        print()
        print("1. INPUT AGENT")
        print("-" * 70)

        input_result = (
            input_agent.analyze_input(
                user_description
            )
        )

        if input_result is None:

            raise RuntimeError(
                "InputAgent returned no result."
            )

        print(
            "✓ InputAgent completed"
        )

        # ====================================================
        # STEP 2 — RESEARCH AGENT
        # ====================================================

        print()
        print("2. RESEARCH AGENT")
        print("-" * 70)

        research_result = (
            research_agent.research(
                input_result
            )
        )

        if research_result is None:

            raise RuntimeError(
                "ResearchAgent returned no result."
            )

        print(
            "✓ ResearchAgent completed"
        )

        # ====================================================
        # EXTRACT RESEARCH DATA
        # ====================================================

        if not isinstance(
            research_result,
            dict
        ):

            raise RuntimeError(
                "ResearchAgent returned an invalid result."
            )

        research_plan = (
            research_result.get(
                "research_plan",
                {}
            )
        )

        image_results = (
            research_result.get(
                "image_results",
                {}
            )
        )

        if not isinstance(
            research_plan,
            dict
        ):
            research_plan = {}

        if not isinstance(
            image_results,
            dict
        ):
            raise RuntimeError(
                "ResearchAgent image results are invalid."
            )

        # ----------------------------------------------------
        # Extract raw and filtered Pexels results.
        # ----------------------------------------------------

        raw_results = (
            image_results.get(
                "raw_results",
                {}
            )
        )

        filtered_results = (
            image_results.get(
                "filtered_results",
                {}
            )
        )

        if not isinstance(
            raw_results,
            dict
        ):
            raw_results = {}

        if not isinstance(
            filtered_results,
            dict
        ):
            filtered_results = {}

        # ====================================================
        # STEP 3 — PREPARE DATABASE DATA
        # ====================================================

        print()
        print("3. PREPARING DATABASE DATA")
        print("-" * 70)

        # ----------------------------------------------------
        # AI description
        # ----------------------------------------------------
        #
        # Use a description/summary supplied by InputAgent
        # when one exists.
        #
        # Otherwise preserve the complete structured AI
        # interpretation as JSON text.
        # ----------------------------------------------------

        if isinstance(
            input_result,
            dict
        ):

            ai_description = (
                input_result.get(
                    "description"
                )
                or input_result.get(
                    "ai_description"
                )
                or input_result.get(
                    "summary"
                )
            )

            if not ai_description:

                ai_description = json.dumps(
                    input_result,
                    ensure_ascii=False
                )

        else:

            ai_description = str(
                input_result
            )

        # ----------------------------------------------------
        # Search components
        # ----------------------------------------------------

        search_components = (
            input_result
        )

        if not isinstance(
            search_components,
            dict
        ):

            search_components = {
                "design_requirements":
                    input_result
            }

        # ----------------------------------------------------
        # Tags
        # ----------------------------------------------------
        #
        # database.py does NOT generate tags.
        #
        # Prefer tags supplied by InputAgent.
        # If none exist, use concepts already generated by the
        # ResearchAgent.
        # ----------------------------------------------------

        tags = []

        if isinstance(
            input_result,
            dict
        ):

            possible_tags = (
                input_result.get(
                    "tags"
                )
            )

            if isinstance(
                possible_tags,
                list
            ):

                tags = [
                    str(tag).strip()
                    for tag in possible_tags
                    if str(tag).strip()
                ]

        if not tags:

            visual_attributes = (
                research_plan.get(
                    "visual_attributes",
                    []
                )
            )

            if isinstance(
                visual_attributes,
                list
            ):

                tags = [
                    str(tag).strip()
                    for tag in visual_attributes
                    if str(tag).strip()
                ]

        if not tags:

            queries = (
                research_plan.get(
                    "primary_search_queries",
                    []
                )
            )

            if isinstance(
                queries,
                list
            ):

                tags = [
                    str(tag).strip()
                    for tag in queries
                    if str(tag).strip()
                ]

        # Keep only the first 8 unique tags.
        unique_tags = []
        seen_tags = set()

        for tag in tags:

            normalized_tag = tag.lower()

            if normalized_tag in seen_tags:
                continue

            seen_tags.add(
                normalized_tag
            )

            unique_tags.append(tag)

            if len(unique_tags) >= 8:
                break

        tags = unique_tags

        # ====================================================
        # STEP 4 — EXTRACT FILTERED IMAGE REFERENCES
        # ====================================================

        print()
        print("4. IMAGE REFERENCES")
        print("-" * 70)

        # Actual structure:
        #
        # image_results
        #     -> filtered_results
        #         -> images
        #
        filtered_images = (
            filtered_results.get(
                "images",
                []
            )
        )

        if not isinstance(
            filtered_images,
            list
        ):
            filtered_images = []

        image_references = []

        for image in filtered_images:

            if not isinstance(
                image,
                dict
            ):
                continue

            image_url = (
                image.get(
                    "image_url"
                )
                or image.get(
                    "url"
                )
            )

            if not image_url:
                continue

            image_references.append({
                "image_url":
                    str(image_url).strip(),

                "source":
                    image.get(
                        "source"
                    )
                    or "Pexels"
            })

        print(
            f"✓ Received "
            f"{len(image_references)} image references"
        )

        # ====================================================
        # STEP 5 — DATABASE
        # ====================================================

        print()
        print("5. DATABASE")
        print("-" * 70)

        # IMPORTANT:
        #
        # user["id"] belongs to user_database.db.
        #
        # database.py has a separate users table.
        # Therefore the authentication user must first be
        # synchronized into database.db.
        #
        # sync_authenticated_user() returns the LOCAL database
        # user ID that is safe to use as searches.user_id.

        database_user_id = (
            database.sync_authenticated_user(
                auth_user_id=user["id"],
                name=user["name"],
                username=user["username"]
            )
        )

        print(
            f"✓ Database user synchronized "
            f"(ID: {database_user_id})"
        )

        # Save the completed search.
        search_id = (
            database.save_search(

                user_id=
                    database_user_id,

                user_description=
                    user_description,

                ai_description=
                    ai_description,

                search_components={
                    "design_requirements":
                        search_components,

                    "research_plan":
                        research_plan
                },

                tags=
                    tags,

                images=
                    image_references
            )
        )

        print(
            f"✓ Search saved successfully "
            f"(ID: {search_id})"
        )

        # ====================================================
        # PIPELINE COMPLETE
        # ====================================================

        pipeline_time = (
            time.perf_counter()
            - pipeline_start
        )

        raw_count = (
            raw_results.get(
                "total_results",
                0
            )
        )

        filtered_count = (
            filtered_results.get(
                "total_after_filtering",
                len(image_references)
            )
        )

        removed_count = (
            filtered_results.get(
                "total_removed",
                0
            )
        )

        print()
        print("=" * 70)
        print("DESIGNFORGE PIPELINE COMPLETE")
        print("=" * 70)

        print(
            f"Raw images: {raw_count}"
        )

        print(
            f"Filtered images: {filtered_count}"
        )

        print(
            f"Saved image references: "
            f"{len(image_references)}"
        )

        print(
            f"Removed images: {removed_count}"
        )

        print(
            f"Time: {pipeline_time:.2f} seconds"
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "message":
                "Design processed successfully.",

            "authenticated":
                True,

            "user": {
                "id":
                    user["id"],

                "name":
                    user["name"],

                "username":
                    user["username"]
            },

            "search_id":
                search_id,

            "pipeline_time":
                round(
                    pipeline_time,
                    2
                ),

            "design_requirements":
                input_result,

            "research":
                research_result,

            "images":
                image_references,

            "statistics": {
                "raw_images":
                    raw_count,

                "filtered_images":
                    filtered_count,

                "saved_image_references":
                    len(image_references),

                "removed_images":
                    removed_count
            }
        })

    except Exception as error:

        pipeline_time = (
            time.perf_counter()
            - pipeline_start
        )

        print()
        print("=" * 70)
        print("DESIGNFORGE PIPELINE ERROR")
        print("=" * 70)

        print(
            f"Error: {error}"
        )

        print(
            f"Time: {pipeline_time:.2f} seconds"
        )

        return jsonify({

            "success": False,

            "message": (
                "DesignForge could not process "
                "your design request."
            ),

            "error":
                str(error)

        }), 500


# ============================================================
# SEARCH HISTORY
# ============================================================

@app.route(
    "/api/search-history",
    methods=["GET"]
)
def search_history():
    """
    Return the logged-in user's DesignForge search history.
    """

    user = (
        get_authenticated_user()
    )

    if user is None:

        return jsonify({
            "success": False,
            "message":
                "You must be logged in."
        }), 401

    try:

        database_user_id = (
            database.sync_authenticated_user(
                auth_user_id=user["id"],
                name=user["name"],
                username=user["username"]
            )
        )

        searches = (
            database.get_user_searches(
                database_user_id
            )
        )

        return jsonify({

            "success": True,

            "user_id":
                user["id"],

            "searches":
                searches

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Could not retrieve search history.",

            "error":
                str(error)

        }), 500


# ============================================================
# INDIVIDUAL SEARCH
# ============================================================

@app.route(
    "/api/search/<int:search_id>",
    methods=["GET"]
)
def get_search(search_id):
    """
    Retrieve one saved DesignForge search.

    The search must belong to the currently logged-in user.
    """

    user = (
        get_authenticated_user()
    )

    if user is None:

        return jsonify({
            "success": False,
            "message":
                "You must be logged in."
        }), 401

    try:

        search = (
            database.get_search(
                search_id
            )
        )

        if search is None:

            return jsonify({
                "success": False,
                "message":
                    "Search not found."
            }), 404

        database_user = (
            database.get_authenticated_database_user(
                user["id"]
            )
        )

        if (
            database_user is None
            or search.get("user_id")
                != database_user["id"]
        ):

            return jsonify({
                "success": False,
                "message":
                    "Search not found."
            }), 404

        return jsonify({

            "success": True,

            "search":
                search

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Could not retrieve the search.",

            "error":
                str(error)

        }), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
