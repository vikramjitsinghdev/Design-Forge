/*
 * ============================================================
 * DESIGNFORGE FRONTEND
 * ============================================================
 *
 * Authentication:
 *
 *     POST /api/login
 *     POST /api/signup
 *     POST /api/logout
 *     GET  /api/session
 *
 * Design:
 *
 *     POST /api/design
 *
 * Search history:
 *
 *     GET /api/search-history
 *
 * ============================================================
 */

"use strict";


/* ============================================================
   API ENDPOINTS
   ============================================================ */

const LOGIN_ENDPOINT = "/api/login";
const SIGNUP_ENDPOINT = "/api/signup";
const LOGOUT_ENDPOINT = "/api/logout";
const SESSION_ENDPOINT = "/api/session";
const DESIGN_ENDPOINT = "/api/design";
const SEARCH_HISTORY_ENDPOINT = "/api/search-history";


/* ============================================================
   AUTH SCENES
   ============================================================ */

const loginScene =
    document.getElementById("loginScene");

const signupScene =
    document.getElementById("signupScene");

const mainScene =
    document.getElementById("mainScene");


/* ============================================================
   LOGIN ELEMENTS
   ============================================================ */

const loginForm =
    document.getElementById("loginForm");

const loginUsername =
    document.getElementById("loginUsername");

const loginPassword =
    document.getElementById("loginPassword");

const loginBtn =
    document.getElementById("loginBtn");

const goToSignupBtn =
    document.getElementById("goToSignupBtn");

const loginMessage =
    document.getElementById("loginMessage");


/* ============================================================
   SIGNUP ELEMENTS
   ============================================================ */

const signupForm =
    document.getElementById("signupForm");

const signupName =
    document.getElementById("signupName");

const signupUsername =
    document.getElementById("signupUsername");

const signupPassword =
    document.getElementById("signupPassword");

const signupBtn =
    document.getElementById("signupBtn");

const backToLoginBtn =
    document.getElementById("backToLoginBtn");

const signupMessage =
    document.getElementById("signupMessage");


/* ============================================================
   MAIN APPLICATION ELEMENTS
   ============================================================ */

const welcomeUser =
    document.getElementById("welcomeUser");

const logoutBtn =
    document.getElementById("logoutBtn");

const promptInput =
    document.getElementById("designPrompt");

const generateBtn =
    document.getElementById("generateBtn");

const loading =
    document.getElementById("loading");

const loadingMessage =
    document.getElementById("loadingMessage");

const errorBox =
    document.getElementById("errorBox");

const results =
    document.getElementById("results");

const requirementsContainer =
    document.getElementById("requirements");

const researchContainer =
    document.getElementById("researchContent");

const imageGrid =
    document.getElementById("imageGrid");

const imageCountLabel =
    document.getElementById("imageCountLabel");

const statsContainer =
    document.getElementById("stats");

const newDesignBtn =
    document.getElementById("newDesignBtn");

const imageModal =
    document.getElementById("imageModal");

const modalImage =
    document.getElementById("modalImage");

const modalClose =
    document.getElementById("modalClose");


/* ============================================================
   STATE
   ============================================================ */

let currentDesign = null;
let currentUser = null;


/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    initializeDesignForge
);


async function initializeDesignForge() {

    setupAuthentication();
    setupDesignFeatures();

    console.log(
        "[DesignForge] Frontend initialized."
    );

    await checkExistingSession();
}


/* ============================================================
   AUTHENTICATION SETUP
   ============================================================ */

function setupAuthentication() {

    loginForm.addEventListener(
        "submit",
        handleLogin
    );

    signupForm.addEventListener(
        "submit",
        handleSignup
    );

    goToSignupBtn.addEventListener(
        "click",
        showSignupScene
    );

    backToLoginBtn.addEventListener(
        "click",
        showLoginScene
    );

    logoutBtn.addEventListener(
        "click",
        handleLogout
    );
}


/* ============================================================
   DESIGN SETUP
   ============================================================ */

function setupDesignFeatures() {

    generateBtn.addEventListener(
        "click",
        generateDesign
    );

    setupExampleButtons();
    setupKeyboardShortcut();
    setupModal();

    newDesignBtn.addEventListener(
        "click",
        resetForNewDesign
    );
}


/* ============================================================
   SCENE MANAGEMENT
   ============================================================ */

function showLoginScene() {

    loginScene.classList.add("active");
    signupScene.classList.remove("active");
    mainScene.classList.remove("active");

    clearAuthMessages();

    setTimeout(() => {
        loginUsername.focus();
    }, 50);
}


function showSignupScene() {

    loginScene.classList.remove("active");
    signupScene.classList.add("active");
    mainScene.classList.remove("active");

    clearAuthMessages();

    signupForm.reset();

    setTimeout(() => {
        signupName.focus();
    }, 50);
}


function showMainScene(user) {

    loginScene.classList.remove("active");
    signupScene.classList.remove("active");
    mainScene.classList.add("active");

    currentUser = user || currentUser;

    if (currentUser) {

        welcomeUser.textContent =
            `Welcome, ${currentUser.name}`;

    } else {

        welcomeUser.textContent = "";

    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* ============================================================
   SESSION CHECK
   ============================================================ */

async function checkExistingSession() {

    try {

        const response =
            await fetch(SESSION_ENDPOINT, {
                method: "GET",
                credentials: "same-origin"
            });

        const data =
            await parseResponse(response);

        if (
            response.ok &&
            data.authenticated &&
            data.user
        ) {

            currentUser = data.user;

            showMainScene(currentUser);

            console.log(
                "[DesignForge] Existing session restored."
            );

            return;
        }

    } catch (error) {

        console.error(
            "[DesignForge] Session check failed:",
            error
        );

    }

    showLoginScene();
}


/* ============================================================
   LOGIN
   ============================================================ */

async function handleLogin(event) {

    event.preventDefault();

    clearAuthMessage(loginMessage);

    const username =
        loginUsername.value.trim();

    const password =
        loginPassword.value;


    if (!username) {

        showAuthMessage(
            loginMessage,
            "Please enter your username."
        );

        loginUsername.focus();

        return;
    }


    if (!password) {

        showAuthMessage(
            loginMessage,
            "Please enter your password."
        );

        loginPassword.focus();

        return;
    }


    setAuthButtonLoading(
        loginBtn,
        true,
        "Checking..."
    );


    try {

        const response =
            await fetch(LOGIN_ENDPOINT, {

                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    username: username,
                    password: password
                })

            });


        const data =
            await parseResponse(response);


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                data.error ||
                "Invalid username or password."
            );
        }


        /*
         * Flask has now created the authenticated
         * session.
         */

        currentUser = data.user || null;


        /*
         * Ask the backend for the actual current
         * user instead of trusting client data.
         */

        const sessionResponse =
            await fetch(
                SESSION_ENDPOINT,
                {
                    credentials: "same-origin"
                }
            );


        const sessionData =
            await parseResponse(
                sessionResponse
            );


        if (
            sessionResponse.ok &&
            sessionData.authenticated
        ) {

            currentUser =
                sessionData.user;

        }


        loginForm.reset();

        showMainScene(currentUser);


        console.log(
            "[DesignForge] Login successful."
        );


    } catch (error) {

        console.error(
            "[DesignForge] Login failed:",
            error
        );

        showAuthMessage(
            loginMessage,
            getFriendlyAuthError(error)
        );


    } finally {

        setAuthButtonLoading(
            loginBtn,
            false,
            "Continue"
        );

    }
}


/* ============================================================
   SIGNUP
   ============================================================ */

async function handleSignup(event) {

    event.preventDefault();

    clearAuthMessage(signupMessage);


    const name =
        signupName.value.trim();

    const username =
        signupUsername.value.trim();

    const password =
        signupPassword.value;


    if (!name) {

        showAuthMessage(
            signupMessage,
            "Please enter your name."
        );

        signupName.focus();

        return;
    }


    if (!username) {

        showAuthMessage(
            signupMessage,
            "Please choose a username."
        );

        signupUsername.focus();

        return;
    }


    if (!password) {

        showAuthMessage(
            signupMessage,
            "Please create a password."
        );

        signupPassword.focus();

        return;
    }


    setAuthButtonLoading(
        signupBtn,
        true,
        "Creating..."
    );


    try {

        const response =
            await fetch(SIGNUP_ENDPOINT, {

                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    name: name,

                    username: username,

                    password: password

                })

            });


        const data =
            await parseResponse(response);


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                data.error ||
                "Could not create the account."
            );
        }


        /*
         * The backend automatically creates
         * the authenticated Flask session
         * after successful signup.
         */

        const sessionResponse =
            await fetch(
                SESSION_ENDPOINT,
                {
                    credentials: "same-origin"
                }
            );


        const sessionData =
            await parseResponse(
                sessionResponse
            );


        if (
            !sessionResponse.ok ||
            !sessionData.authenticated
        ) {

            throw new Error(
                "Account was created, but the login session could not be established."
            );
        }


        currentUser =
            sessionData.user;


        signupForm.reset();


        showMainScene(
            currentUser
        );


        console.log(
            "[DesignForge] Signup successful."
        );


    } catch (error) {

        console.error(
            "[DesignForge] Signup failed:",
            error
        );

        showAuthMessage(
            signupMessage,
            getFriendlyAuthError(error)
        );


    } finally {

        setAuthButtonLoading(
            signupBtn,
            false,
            "Continue"
        );

    }
}


/* ============================================================
   LOGOUT
   ============================================================ */

async function handleLogout() {

    logoutBtn.disabled = true;

    try {

        const response =
            await fetch(
                LOGOUT_ENDPOINT,
                {
                    method: "POST",
                    credentials: "same-origin"
                }
            );


        const data =
            await parseResponse(response);


        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Logout failed."
            );
        }


    } catch (error) {

        console.error(
            "[DesignForge] Logout failed:",
            error
        );

    } finally {

        currentUser = null;

        clearResults();
        clearError();

        promptInput.value = "";

        logoutBtn.disabled = false;

        showLoginScene();

        loginForm.reset();

        console.log(
            "[DesignForge] Logged out."
        );
    }
}


/* ============================================================
   AUTH UI
   ============================================================ */

function showAuthMessage(
    element,
    message,
    success = false
) {

    element.textContent =
        message;

    element.classList.toggle(
        "auth-success",
        success
    );

    element.classList.add(
        "active"
    );
}


function clearAuthMessage(element) {

    element.textContent = "";

    element.classList.remove(
        "active"
    );

    element.classList.remove(
        "auth-success"
    );
}


function clearAuthMessages() {

    clearAuthMessage(
        loginMessage
    );

    clearAuthMessage(
        signupMessage
    );
}


function setAuthButtonLoading(
    button,
    loadingState,
    text
) {

    button.disabled =
        loadingState;

    button.textContent =
        text;
}


/* ============================================================
   AUTH ERROR HANDLING
   ============================================================ */

function getFriendlyAuthError(error) {

    if (!error) {
        return "Something went wrong.";
    }


    if (
        error instanceof TypeError &&
        error.message
            .toLowerCase()
            .includes("fetch")
    ) {

        return (
            "Could not connect to the DesignForge backend. " +
            "Make sure Flask is running."
        );
    }


    return (
        error.message ||
        "Authentication could not be completed."
    );
}


/* ============================================================
   GENERATE DESIGN
   ============================================================ */

async function generateDesign() {

    const prompt =
        promptInput.value.trim();


    clearError();


    if (!prompt) {

        showError(
            "Please describe the design you want to create."
        );

        promptInput.focus();

        return;
    }


    if (prompt.length < 10) {

        showError(
            "Please provide a little more detail about your design."
        );

        promptInput.focus();

        return;
    }


    setLoading(true);

    clearResults();


    try {

        updateLoadingMessage(
            "Analyzing your design requirements..."
        );


        /*
         * IMPORTANT:
         *
         * app.py expects:
         *
         * {
         *     "description": "..."
         * }
         */

        const response =
            await fetch(
                DESIGN_ENDPOINT,
                {

                    method: "POST",

                    credentials: "same-origin",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        description: prompt

                    })

                }
            );


        updateLoadingMessage(
            "Building visual research..."
        );


        const data =
            await parseResponse(
                response
            );


        if (
            response.status === 401 ||
            data.authenticated === false
        ) {

            currentUser = null;

            showLoginScene();

            throw new Error(
                "Your session has expired. Please log in again."
            );
        }


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                data.error ||
                "DesignForge could not complete the request."
            );
        }


        updateLoadingMessage(
            "Preparing your design direction..."
        );


        currentDesign =
            data;


        renderResults(
            data
        );


        results.classList.add(
            "active"
        );


        setTimeout(() => {

            results.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);


    } catch (error) {

        console.error(
            "[DesignForge] Request failed:",
            error
        );


        showError(
            getFriendlyError(error)
        );


    } finally {

        setLoading(false);

    }
}


/* ============================================================
   RESPONSE PARSER
   ============================================================ */

async function parseResponse(
    response
) {

    const text =
        await response.text();


    try {

        return JSON.parse(text);

    } catch (error) {

        console.error(
            "[DesignForge] Invalid JSON response:",
            text
        );


        throw new Error(
            "The backend returned an invalid response."
        );
    }
}


/* ============================================================
   RENDER RESULTS
   ============================================================ */

function renderResults(data) {

    /*
     * Support the current frontend response structure
     * and the structure returned by the new app.py.
     */

    renderRequirements(
        data.design_requirements || {}
    );


    const researchPlan =
        data.research_plan ||
        (
            data.research &&
            data.research.research_plan
        ) ||
        {};


    const imageResults =
        data.image_results ||
        (
            data.research &&
            data.research.image_results
        ) ||
        data.images ||
        {};


    const statistics =
        data.statistics ||
        {};


    const timing =
        data.timing ||
        {};


    renderResearchPlan(
        researchPlan
    );


    renderImages(
        imageResults
    );


    renderStatistics(
        statistics,
        timing
    );
}


/* ============================================================
   REQUIREMENTS
   ============================================================ */

function renderRequirements(
    requirements
) {

    requirementsContainer.innerHTML = "";


    addRequirement(
        "Category",
        requirements.category
    );


    addRequirement(
        "Audience",
        requirements.audience
    );


    addRequirement(
        "Complexity",
        requirements.complexity
    );


    addRequirement(
        "Purpose",
        requirements.purpose
    );


    addListRequirement(
        "Colors",
        requirements.colors
    );


    addListRequirement(
        "Style",
        requirements.style
    );


    addListRequirement(
        "Silhouette",
        requirements.silhouette
    );


    addListRequirement(
        "Required Features",
        requirements.required_features
    );


    addListRequirement(
        "Excluded Features",
        requirements.excluded_features,
        true
    );


    addListRequirement(
        "Materials",
        requirements.materials
    );


    if (
        requirements.confidence !== undefined
    ) {

        addRequirement(
            "Analysis Confidence",
            `${Math.round(
                Number(
                    requirements.confidence
                ) * 100
            )}%`
        );

    }
}


function addRequirement(
    label,
    value
) {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        return;
    }


    const element =
        document.createElement("div");


    element.className =
        "requirement";


    const labelElement =
        document.createElement("div");


    labelElement.className =
        "requirement-label";


    labelElement.textContent =
        label;


    const valueElement =
        document.createElement("div");


    valueElement.className =
        "requirement-value";


    valueElement.textContent =
        String(value);


    element.appendChild(
        labelElement
    );


    element.appendChild(
        valueElement
    );


    requirementsContainer.appendChild(
        element
    );
}


function addListRequirement(
    label,
    values,
    excluded = false
) {

    if (
        !Array.isArray(values) ||
        values.length === 0
    ) {

        return;
    }


    const element =
        document.createElement("div");


    element.className =
        "requirement";


    const labelElement =
        document.createElement("div");


    labelElement.className =
        "requirement-label";


    labelElement.textContent =
        label;


    const tagList =
        document.createElement("div");


    tagList.className =
        "tag-list";


    values.forEach(
        (value) => {

            const tag =
                document.createElement("span");


            tag.className =
                excluded
                    ? "tag excluded"
                    : "tag";


            tag.textContent =
                String(value);


            tagList.appendChild(
                tag
            );

        }
    );


    element.appendChild(
        labelElement
    );


    element.appendChild(
        tagList
    );


    requirementsContainer.appendChild(
        element
    );
}


/* ============================================================
   RESEARCH PLAN
   ============================================================ */

function renderResearchPlan(
    plan
) {

    researchContainer.innerHTML =
        "";


    if (
        plan.research_objective
    ) {

        const objective =
            document.createElement("p");


        objective.className =
            "research-objective";


        objective.textContent =
            plan.research_objective;


        researchContainer.appendChild(
            objective
        );
    }


    if (
        Array.isArray(
            plan.primary_search_queries
        ) &&
        plan.primary_search_queries.length > 0
    ) {

        addResearchSection(
            "Primary search queries",
            plan.primary_search_queries,
            "query"
        );
    }


    if (
        Array.isArray(
            plan.alternative_search_queries
        ) &&
        plan.alternative_search_queries.length > 0
    ) {

        addResearchSection(
            "Alternative search queries",
            plan.alternative_search_queries,
            "query"
        );
    }


    if (
        Array.isArray(
            plan.ranking_priorities
        ) &&
        plan.ranking_priorities.length > 0
    ) {

        addResearchSection(
            "Ranking priorities",
            plan.ranking_priorities,
            "tag"
        );
    }


    if (
        Array.isArray(
            plan.hard_requirements
        ) &&
        plan.hard_requirements.length > 0
    ) {

        addResearchSection(
            "Hard requirements",
            plan.hard_requirements,
            "tag"
        );
    }


    if (
        Array.isArray(
            plan.hard_exclusions
        ) &&
        plan.hard_exclusions.length > 0
    ) {

        addResearchSection(
            "Hard exclusions",
            plan.hard_exclusions,
            "tag excluded"
        );
    }
}


function addResearchSection(
    title,
    values,
    className
) {

    const sectionTitle =
        document.createElement("div");


    sectionTitle.style.marginTop =
        "20px";


    sectionTitle.style.fontWeight =
        "700";


    sectionTitle.textContent =
        title;


    const container =
        document.createElement("div");


    if (
        className === "query"
    ) {

        container.className =
            "query-list";


        values.forEach(
            (value) => {

                const item =
                    document.createElement("div");


                item.className =
                    "query";


                item.textContent =
                    String(value);


                container.appendChild(
                    item
                );

            }
        );

    } else {

        container.className =
            "tag-list";


        values.forEach(
            (value) => {

                const item =
                    document.createElement("span");


                item.className =
                    className;


                item.textContent =
                    String(value);


                container.appendChild(
                    item
                );

            }
        );
    }


    researchContainer.appendChild(
        sectionTitle
    );


    researchContainer.appendChild(
        container
    );
}


/* ============================================================
   IMAGES
   ============================================================ */

function renderImages(
    imageResults
) {

    imageGrid.innerHTML =
        "";


    let images = [];


    /*
     * Current Pexels structure.
     */

    if (
        imageResults &&
        imageResults.filtered_results &&
        Array.isArray(
            imageResults
                .filtered_results
                .images
        )
    ) {

        images =
            imageResults
                .filtered_results
                .images;
    }


    /*
     * Direct image list support.
     */

    else if (
        Array.isArray(
            imageResults
        )
    ) {

        images =
            imageResults;
    }


    /*
     * New app.py structure.
     */

    else if (
        imageResults &&
        Array.isArray(
            imageResults.images
        )
    ) {

        images =
            imageResults.images;
    }


    imageCountLabel.textContent =
        `${images.length} reference${
            images.length === 1
                ? ""
                : "s"
        }`;


    if (
        images.length === 0
    ) {

        const noImages =
            document.createElement("div");


        noImages.className =
            "no-images";


        noImages.textContent =
            "No visual references were returned.";


        imageGrid.appendChild(
            noImages
        );


        return;
    }


    images.forEach(
        (image) => {

            if (
                !image ||
                !image.image_url
            ) {

                return;
            }


            const card =
                document.createElement("div");


            card.className =
                "image-card";


            const imageElement =
                document.createElement("img");


            imageElement.src =
                image.image_url;


            imageElement.alt =
                imageDescription(
                    image
                );


            imageElement.loading =
                "lazy";


            imageElement.addEventListener(
                "error",
                () => {

                    card.remove();

                    updateImageCount();

                }
            );


            imageElement.addEventListener(
                "click",
                () => {

                    openImageModal(
                        image.image_url,
                        imageDescription(
                            image
                        )
                    );

                }
            );


            const overlay =
                document.createElement("div");


            overlay.className =
                "image-overlay";


            const link =
                document.createElement("a");


            link.href =
                image.pexels_url ||
                image.original_url ||
                image.image_url;


            link.target =
                "_blank";


            link.rel =
                "noopener noreferrer";


            link.textContent =
                image.photographer
                    ? `Photo by ${image.photographer}`
                    : "View source";


            overlay.appendChild(
                link
            );


            card.appendChild(
                imageElement
            );


            card.appendChild(
                overlay
            );


            imageGrid.appendChild(
                card
            );

        }
    );


    updateImageCount();
}


function updateImageCount() {

    const count =
        imageGrid.querySelectorAll(
            ".image-card"
        ).length;


    imageCountLabel.textContent =
        `${count} reference${
            count === 1
                ? ""
                : "s"
        }`;
}


function imageDescription(
    image
) {

    if (image.query) {

        return (
            `Design reference: ${image.query}`
        );
    }


    return "Design reference";
}


/* ============================================================
   STATISTICS
   ============================================================ */

function renderStatistics(
    statistics,
    timing
) {

    statsContainer.innerHTML =
        "";


    addStat(
        statistics.raw_images ?? 0,
        "Raw images"
    );


    addStat(
        statistics.filtered_images ?? 0,
        "Filtered images"
    );


    addStat(
        statistics.removed_images ?? 0,
        "Removed images"
    );


    if (
        timing.total_seconds !== undefined
    ) {

        addStat(
            `${timing.total_seconds}s`,
            "Total time"
        );

    } else if (
        window.currentDesign &&
        window.currentDesign.pipeline_time !== undefined
    ) {

        addStat(
            `${window.currentDesign.pipeline_time}s`,
            "Total time"
        );

    } else {

        addStat(
            "—",
            "Total time"
        );
    }


    if (
        timing.input_agent_seconds !== undefined
    ) {

        addStat(
            `${timing.input_agent_seconds}s`,
            "Input Agent"
        );
    }


    if (
        timing.research_pipeline_seconds !== undefined
    ) {

        addStat(
            `${timing.research_pipeline_seconds}s`,
            "Research Pipeline"
        );
    }
}


function addStat(
    value,
    label
) {

    const element =
        document.createElement("div");


    element.className =
        "stat";


    const valueElement =
        document.createElement("div");


    valueElement.className =
        "stat-value";


    valueElement.textContent =
        String(value);


    const labelElement =
        document.createElement("div");


    labelElement.className =
        "stat-label";


    labelElement.textContent =
        label;


    element.appendChild(
        valueElement
    );


    element.appendChild(
        labelElement
    );


    statsContainer.appendChild(
        element
    );
}


/* ============================================================
   LOADING STATE
   ============================================================ */

function setLoading(
    isLoading
) {

    loading.classList.toggle(
        "active",
        isLoading
    );


    generateBtn.disabled =
        isLoading;


    const buttonText =
        generateBtn.querySelector(
            "span"
        );


    if (buttonText) {

        buttonText.textContent =
            isLoading
                ? "Generating"
                : "Generate";
    }
}


function updateLoadingMessage(
    message
) {

    loadingMessage.textContent =
        message;
}


/* ============================================================
   ERROR HANDLING
   ============================================================ */

function showError(
    message
) {

    errorBox.textContent =
        message;


    errorBox.classList.add(
        "active"
    );


    errorBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function clearError() {

    errorBox.textContent =
        "";


    errorBox.classList.remove(
        "active"
    );
}


function getFriendlyError(
    error
) {

    if (!error) {

        return "Something went wrong.";
    }


    if (
        error instanceof TypeError &&
        error.message
            .toLowerCase()
            .includes("fetch")
    ) {

        return (
            "Could not connect to the DesignForge backend. " +
            "Make sure Flask is running on " +
            "http://127.0.0.1:5000."
        );
    }


    return (
        error.message ||
        "DesignForge could not complete the request."
    );
}


/* ============================================================
   CLEAR RESULTS
   ============================================================ */

function clearResults() {

    results.classList.remove(
        "active"
    );


    requirementsContainer.innerHTML =
        "";


    researchContainer.innerHTML =
        "";


    imageGrid.innerHTML =
        "";


    statsContainer.innerHTML =
        "";


    currentDesign =
        null;
}


/* ============================================================
   NEW DESIGN
   ============================================================ */

function resetForNewDesign() {

    clearResults();

    clearError();

    promptInput.value =
        "";

    promptInput.focus();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* ============================================================
   EXAMPLE PROMPTS
   ============================================================ */

function setupExampleButtons() {

    const buttons =
        document.querySelectorAll(
            ".example-btn"
        );


    buttons.forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    const prompt =
                        button.dataset.prompt;


                    if (!prompt) {

                        return;
                    }


                    promptInput.value =
                        prompt;


                    promptInput.focus();


                    promptInput.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });

                }
            );

        }
    );
}


/* ============================================================
   KEYBOARD SHORTCUT
   ============================================================ */

function setupKeyboardShortcut() {

    promptInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                generateDesign();
            }

        }
    );
}


/* ============================================================
   IMAGE MODAL
   ============================================================ */

function setupModal() {

    modalClose.addEventListener(
        "click",
        closeImageModal
    );


    imageModal.addEventListener(
        "click",
        (event) => {

            if (
                event.target === imageModal
            ) {

                closeImageModal();
            }

        }
    );


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                imageModal.classList.contains(
                    "active"
                )
            ) {

                closeImageModal();
            }

        }
    );
}


function openImageModal(
    imageUrl,
    altText
) {

    modalImage.src =
        imageUrl;


    modalImage.alt =
        altText;


    imageModal.classList.add(
        "active"
    );
}


function closeImageModal() {

    imageModal.classList.remove(
        "active"
    );


    modalImage.src =
        "";
}


/* ============================================================
   DEBUG ACCESS
   ============================================================ */

window.DesignForge = {

    getCurrentDesign:
        () => currentDesign,

    getCurrentUser:
        () => currentUser,

    generate:
        generateDesign,

    logout:
        handleLogout

};
