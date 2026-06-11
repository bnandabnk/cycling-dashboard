# ============================================================
# CYCLING HYDRATION & RECOVERY DASHBOARD
# File: app.py  —  Strava-connected edition
#
# WHAT THIS FILE IS:
# This is a Python script — a text file full of instructions that the computer
# reads top-to-bottom and executes one line at a time.
#
# WHAT THIS APP DOES:
# It is a web dashboard for cyclists. It connects to your Strava account,
# pulls your real ride history, and uses that data to:
#   1. Show you educational cycling tips
#   2. Let you plan your next ride (distance + time)
#   3. Tell you how much water and food to take
#   4. Show a table of your past rides with intensity colours
#
# HOW TO RUN IT:
# Open a terminal and type:  streamlit run app.py
# Your browser will open automatically showing the dashboard.
# ============================================================


# ============================================================
# IMPORTS — LOADING EXTERNAL TOOLS ("LIBRARIES")
#
# Think of imports like opening a toolbox before you start working.
# Python by itself can do basic maths and text. Libraries add extra
# powerful features so you don't have to build everything from scratch.
# ============================================================

# streamlit — the library that turns this Python script into a web app.
# Every line that starts with "st." draws something on the web page:
# buttons, tables, text, metrics, etc.
# Without streamlit this would just be a script with no visual interface.
import streamlit as st

# pandas — the library for working with data tables (like Excel in code).
# It lets you create, sort, filter, and style rows-and-columns of data.
# We use it to display the past rides table at the bottom of the dashboard.
import pandas as pd

# requests — the library for sending messages to the internet and receiving replies.
# Think of it like a messenger: we send a request to Strava's servers
# ("give me this athlete's rides"), and Strava sends back the data.
import requests

# datetime and date — built-in Python tools for working with time.
# "datetime" handles full date+time (e.g. 2026-06-08 14:30:00).
# "date" handles date-only (e.g. 2026-06-08).
# We use them to calculate "how many days since your last ride."
from datetime import datetime, date

import urllib.parse

# This line configures the browser tab when someone opens the app.
# st.set_page_config() must be the very first streamlit command in the file.
st.set_page_config(
    page_title="Cycling Dashboard",  # The text shown in the browser tab at the top
    page_icon="🚴",                   # The small icon shown next to the tab title
    layout="wide"                     # "wide" uses the full screen width; default is a narrow centered column
)


# ============================================================
# SECTION 1: CYCLING TIPS DATA
#
# This section defines a big list of cycling knowledge.
# Each item in the list is a dictionary (a labelled data package)
# with two pieces of information: the tip text and its category.
#
# A "list" in Python is a collection of items, written with square brackets [].
# A "dictionary" is a set of key:value pairs, written with curly braces {}.
# Example: {"name": "Nanda", "age": 25}  ← a dictionary with two entries.
# ============================================================

# cycling_tips_categorized is a variable (a named storage box) that holds
# all the tip dictionaries in one big list.
cycling_tips_categorized = [
    # --- TRAINING ---
    # Each line below is one dictionary: {"tip": "the tip text", "category": "category name"}
    # The category is used to group tips by topic.
    {"tip": "What is Cadence? Cadence is your pedaling rate, measured in Revolutions Per Minute (RPM). Aim for 85–95 RPM to save your leg muscles and rely more on your cardiovascular system.", "category": "Training"},
    {"tip": "What are Watts? A Watt is a measure of power (energy transferred over time). In cycling, it represents how much raw force you are putting into the pedals.", "category": "Training"},
    {"tip": "What is FTP? Functional Threshold Power (FTP) is the highest average power (in Watts) you can sustain for one hour without fatiguing.", "category": "Training"},
    {"tip": "What is VO2 Max? It is the maximum amount of oxygen your body can utilize during intense exercise. Higher VO2 Max means better endurance.", "category": "Training"},
    {"tip": "What is TSS? Training Stress Score (TSS) measures the workload of a ride based on duration and intensity. It helps you manage fatigue over a training week.", "category": "Training"},
    {"tip": "Base miles build your aerobic engine. Spend 80% of your training time at a low, conversational pace (Zone 2). This is where real endurance is built.", "category": "Training"},
    {"tip": "Intervals raise your ceiling. Spend 20% of your training doing high-intensity efforts to push your FTP and VO2 Max higher.", "category": "Training"},
    {"tip": "Consistency beats epic rides. Riding 1 hour four times a week builds more fitness than one massive 4-hour ride on Sunday.", "category": "Training"},
    {"tip": "Your brain will tell you to quit long before your legs actually fail. Endurance is highly psychological — train your mind alongside your body.", "category": "Training"},
    {"tip": "Core strength is cycling strength. A strong core prevents lower back pain and stabilizes your pelvis for better power transfer to the pedals.", "category": "Training"},
    {"tip": "Tapering: Reduce your riding volume by 30–50% in the week leading up to a major event. This sheds fatigue and lets your fitness peak on race day.", "category": "Training"},
    {"tip": "What is a 'century'? A century ride refers to completing 100 miles (160 km) — a major milestone for endurance cyclists.", "category": "Training"},

    # --- NUTRITION ---
    {"tip": "What is Bonking? 'Bonking' or 'hitting the wall' happens when your body completely depletes its glycogen (carbohydrate) stores, causing extreme fatigue.", "category": "Nutrition"},
    {"tip": "Eat before you are hungry, drink before you are thirsty. Your body can only process about 60–90 grams of carbs per hour — exceeding this causes gut issues.", "category": "Nutrition"},
    {"tip": "Protein is for recovery, carbs are for fuel. Consume a 3:1 ratio of carbs to protein within 30 minutes after a hard ride to kickstart muscle repair.", "category": "Nutrition"},
    {"tip": "Sodium is critical. You lose electrolytes through sweat. Add electrolyte tabs or a pinch of salt to your water on rides longer than 90 minutes.", "category": "Nutrition"},
    {"tip": "Caffeine is a proven performance enhancer. A coffee or caffeine gel 45 minutes before a hard ride measurably lowers your perceived exertion.", "category": "Nutrition"},
    {"tip": "Hydration baseline: Drink one bottle (500 ml) per hour of riding. In hot weather or at high intensity, increase this to 750 ml per hour.", "category": "Nutrition"},
    {"tip": "Train your gut. Practice eating the specific gels, bars, and drinks you plan to use on race day to avoid stomach cramps and nausea.", "category": "Nutrition"},

    # --- TECHNIQUE ---
    {"tip": "Aerodynamic drag accounts for 70–90% of the resistance you feel at speed. Riding in the drops or aero hoods saves more energy than reducing bike weight.", "category": "Technique"},
    {"tip": "Drafting behind another cyclist can save you up to 30% of your energy output. Stay in their slipstream but leave a safe distance.", "category": "Technique"},
    {"tip": "Don't grip the handlebars too tightly. A relaxed upper body absorbs road shock, reduces fatigue, and saves energy over long rides.", "category": "Technique"},
    {"tip": "Look where you want to go, not where you are. Your bike follows your eyes — this is especially important when descending or cornering at speed.", "category": "Technique"},
    {"tip": "Brake before the corner, not in it. Trail off the brakes as you lean the bike into the turn to maintain traction and control.", "category": "Technique"},
    {"tip": "Pace your climbs. Don't attack the bottom of a hill; start easy and build your effort so you don't blow up halfway and crawl to the top.", "category": "Technique"},
    {"tip": "Headwinds are just invisible hills. Drop a gear, get aerodynamic, and accept a lower speed rather than burning out trying to hold your average.", "category": "Technique"},
    {"tip": "Shift gears before you need to. Anticipate climbs and shift into an easier gear before the tension on the pedals becomes too high to shift cleanly.", "category": "Technique"},
    {"tip": "Stand up on the pedals every 15–20 minutes to relieve pressure on your sit bones and restore blood flow to your legs.", "category": "Technique"},
    {"tip": "When climbing out of the saddle, click into a harder gear first. This compensates for the lower cadence of standing and keeps power consistent.", "category": "Technique"},
    {"tip": "Keep your elbows slightly bent at all times. Locked elbows transmit every road bump directly to your neck, shoulders, and lower back.", "category": "Technique"},
    {"tip": "Smooth is fast. Jerky pedal strokes waste energy. Focus on a full circular motion — push forward at the top, pull back at the bottom.", "category": "Technique"},
    {"tip": "A tailwind going out means a headwind coming back. Always plan your pacing and nutrition around the wind direction.", "category": "Technique"},
    {"tip": "What is an 'echelon'? A staggered formation used by group riders to shelter from crosswinds — each rider overlaps the rider ahead and slightly to the side.", "category": "Technique"},
    {"tip": "What is a 'pull'? Taking a pull means riding at the front of a group, bearing the full brunt of wind resistance so others can draft behind you.", "category": "Technique"},

    # --- EQUIPMENT ---
    {"tip": "Tire pressure matters. Lower pressure (70–85 psi) on wider tires often rolls faster in real-world conditions because it better absorbs road vibrations.", "category": "Equipment"},
    {"tip": "Always clean and lube your chain every 150–200 km. A dirty, dry drivetrain can waste up to 5 Watts of power — that's significant at any speed.", "category": "Equipment"},
    {"tip": "Avoid 'cross-chaining' — riding in the big front ring and the biggest rear cog simultaneously. It angles the chain, causing wear and reducing efficiency.", "category": "Equipment"},
    {"tip": "Saddle height: When your pedal is at the very bottom (6 o'clock position), your knee should have a slight bend of about 25–30 degrees. Too low = knee pain.", "category": "Equipment"},
    {"tip": "Chamois cream reduces friction between skin and pad. Apply it directly to the chamois for rides over 2 hours to prevent saddle sores.", "category": "Equipment"},
    {"tip": "Never wear underwear under cycling shorts. Cotton seams will cause severe chafing that gets worse with every pedal stroke.", "category": "Equipment"},
    {"tip": "Knee pain diagnosis: Front-of-knee pain usually means your saddle is too low. Back-of-knee pain usually means your saddle is too high.", "category": "Equipment"},
    {"tip": "Cleat position: The ball of your foot should sit directly over the pedal spindle. Correct cleat position prevents knee tracking problems.", "category": "Equipment"},
    {"tip": "Check your tires carefully after every ride by running your thumb along the tread. Remove embedded glass shards before they work into the tube.", "category": "Equipment"},
    {"tip": "Learn to change a flat tire quickly at home first — practice at least three times — so you aren't panicking on the roadside when it happens.", "category": "Equipment"},

    # --- RECOVERY ---
    {"tip": "Post-ride recovery starts in the last 15 minutes of your ride. Spin easily in a light gear to flush lactate from your legs before stopping.", "category": "Recovery"},
    {"tip": "Sleep is the ultimate performance-enhancing drug. Human Growth Hormone (HGH) is released during deep sleep to repair muscle tissue and consolidate fitness gains.", "category": "Recovery"},
    {"tip": "Active recovery (a very light, easy spin at Zone 1) promotes blood flow and clears metabolic waste products faster than complete rest.", "category": "Recovery"},
    {"tip": "Stretch your hip flexors and hamstrings after every ride. Cycling shortens these muscles due to the constant forward-leaning, flexed-hip posture.", "category": "Recovery"},

    # --- SAFETY ---
    {"tip": "Wear bright, high-visibility colors and use a rear red light even during the day. Being seen is your single most important safety behaviour on the road.", "category": "Safety"},

    # --- GENERAL ---
    {"tip": "Remember to enjoy the view. We ride bikes for fitness and performance, yes — but also for the joy, the freedom, and the places the bike takes us.", "category": "General"},
]

# TIP_CATEGORIES is a list of all the category names.
# "All" at the front means "show every tip regardless of category."
# This list could be used in future to add a category filter dropdown.
TIP_CATEGORIES = ["All", "Training", "Nutrition", "Technique", "Equipment", "Recovery", "Safety", "General"]


# ============================================================
# SECTION 2: STRAVA API LAYER
#
# "API" = Application Programming Interface.
# It is a structured way for two programs to talk to each other.
# Strava has a public API: if you have the right password (token),
# you can ask Strava for data about your rides.
#
# Think of it like phoning a bank: you give your account number (token),
# and the bank (Strava) reads your balance (ride data) back to you.
# ============================================================

# The base URL for all Strava API requests.
# Every request to Strava starts with this address, then we add
# the specific endpoint, e.g. "athlete/activities" for the ride list.
STRAVA_BASE      = "https://www.strava.com/api/v3"

# The URL used specifically for getting/refreshing login tokens.
# A "token" is like a temporary password that Strava gives you after login.
# It expires every 6 hours, so we need to renew it automatically.
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

# A Python "set" (curly braces, like a list but faster to search) of
# the Strava activity type names that count as cycling.
# "Ride" = outdoor ride, "VirtualRide" = indoor trainer (e.g. Zwift),
# "EBikeRide" = electric bike ride.
# We use this to filter out runs, swims, etc. from the activity list.
CYCLING_TYPES    = {"Ride", "VirtualRide", "EBikeRide"}

# A special marker string (called a "sentinel") we return when Strava
# says "permission denied" specifically because of missing scope.
# Using a named constant like this (instead of typing the raw string
# in multiple places) means if we ever rename it, we only change it here.
NEEDS_REAUTH     = "NEEDS_REAUTH"

# The URL Strava redirects to after the user authorizes.
# Must match the domain registered in the Strava developer portal.
REDIRECT_URI = "https://cycling-dashboard-cocnsx37vepb2nuvetef4x.streamlit.app/"


# ============================================================
# FUNCTION: _strava_get
#
# A "function" is a reusable block of code given a name.
# Instead of copying the same code every time we want to fetch from Strava,
# we define it once here and then call it by name wherever we need it.
#
# The underscore prefix (_strava_get) is a Python convention meaning
# "this is an internal helper — not meant to be called from outside this file."
#
# @st.cache_data(ttl=300)
# This line above the function is called a "decorator."
# It tells streamlit: "Remember (cache) the result of this function for 300 seconds
# (5 minutes). If the same request is made again within 5 minutes, return the
# saved result instead of hitting Strava's servers again."
# This prevents hammering Strava with requests every time the page refreshes.
# ============================================================
@st.cache_data(ttl=300)
def _strava_get(endpoint, token, per_page=0):
    # "endpoint" = which data to fetch (e.g. "athlete/activities")
    # "token" = the temporary Strava password for this user
    # "per_page=0" = how many results to return; 0 means use Strava's default
    # The "= 0" part means it defaults to 0 if the caller doesn't specify it

    # Build the "params" dictionary — extra options sent with the request.
    # If per_page is non-zero, add it; otherwise send an empty dict (no extra options).
    # The syntax "X if condition else Y" means: use X when condition is True, Y when False.
    params = {"per_page": per_page} if per_page else {}

    # "try / except" is error handling — "try" to run the code inside,
    # but if it crashes with a RequestException (e.g. no internet), jump to "except"
    # and return safe dummy values instead of crashing the whole app.
    try:
        # requests.get() sends an HTTP GET request — the standard way browsers/apps
        # ask a server for data (as opposed to POST, which sends data to the server).
        resp = requests.get(
            # Build the full URL by joining the base URL with the endpoint name.
            # The f"..." syntax is an "f-string" — it inserts variable values into text.
            # Example: if endpoint = "athlete/activities", this becomes
            #          "https://www.strava.com/api/v3/athlete/activities"
            f"{STRAVA_BASE}/{endpoint}",

            # "headers" are extra information sent alongside the request.
            # The Authorization header is how we prove to Strava who we are.
            # "Bearer {token}" is a standard format meaning "I have this token as proof."
            headers={"Authorization": f"Bearer {token}"},

            # The extra URL parameters (e.g. per_page=30).
            params=params,

            # timeout=10 means: if Strava doesn't respond within 10 seconds, give up.
            # Without a timeout, the app could hang forever waiting for a response.
            timeout=10,
        )

        # Return two values at once (Python can do this!):
        # 1. resp.status_code — a number Strava sends back to say how the request went.
        #    200 = success, 401 = not logged in, 500 = Strava server error, etc.
        # 2. resp.json() if resp.ok else None
        #    resp.ok is True when status_code is 200–299 (success range).
        #    resp.json() converts the response text (JSON format) into a Python dictionary.
        #    If the request failed, return None (Python's way of saying "nothing / empty").
        return resp.status_code, resp.json() if resp.ok else None

    # If any network error occurs (no internet, Strava down, DNS failure, etc.)
    # catch the error quietly and return status 0 with no data.
    # Status 0 is not a real HTTP code — we use it as our own "connection failed" signal.
    except requests.exceptions.RequestException:
        return 0, None


# ============================================================
# FUNCTION: _refresh_strava_token
#
# Strava access tokens expire after 6 hours for security.
# When that happens, we use the "refresh token" (a longer-lived token)
# to get a brand new access token without making the user log in again.
# This is part of the "OAuth 2.0" security standard used by most big apps.
# ============================================================
def _refresh_strava_token():
    refresh_token = st.session_state.get("strava_refresh_token")
    if not refresh_token:
        return None
    creds = st.secrets["strava"]
    try:
        resp = requests.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id":     creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": refresh_token,
                "grant_type":    "refresh_token",
            },
            timeout=10,
        )
        if resp.ok:
            d = resp.json()
            if d.get("refresh_token"):
                st.session_state.strava_refresh_token = d["refresh_token"]
            return d.get("access_token")
        return None
    except requests.exceptions.RequestException:
        return None


# ============================================================
# FUNCTION: exchange_auth_code
#
# This is only used once during the very first Strava connection setup.
# When a user clicks "Authorize" on Strava's website, Strava gives them
# a short-lived one-time "authorization code" (valid for ~10 minutes).
# We swap that code here for real access + refresh tokens.
# ============================================================
def exchange_auth_code(code):
    # "code" is the one-time authorization code the user pastes from the URL bar.

    creds = st.secrets["strava"]  # Load app credentials from secrets file

    try:
        resp = requests.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id":     creds["client_id"],     # Our app's Strava ID
                "client_secret": creds["client_secret"], # Our app's Strava password
                "code":          code,                   # The one-time code from the user
                "grant_type":    "authorization_code",   # Tells Strava: "I have a fresh code"
            },
            timeout=10,
        )

        if resp.ok:
            # Parse the response JSON into a Python dictionary called "d"
            d = resp.json()

            # Return three values at once: access token, refresh token, and scope.
            # "scope" is a string like "read,activity:read_all" that lists what
            # permissions were granted. We check this to confirm activity access.
            # .get("key", default) returns "default" if the key is missing.
            return d.get("access_token"), d.get("refresh_token"), d.get("scope", "")

        # If Strava replied with an error, return three None/empty values.
        return None, None, ""

    except requests.exceptions.RequestException:
        # Network failure — return empty values safely.
        return None, None, ""




# ============================================================
# FUNCTION: load_strava_data
#
# This is the main data-loading function. It:
#   1. Gets an access token (refreshing it if expired)
#   2. Fetches up to 30 recent activities from Strava
#   3. Filters for cycling-only activities
#   4. Converts the raw Strava data into the format our app uses
#   5. Returns the athlete profile, the ride list, and any error message
#
# It returns THREE values: (athlete, past_rides, error_message)
# The caller unpacks them: athlete, past_rides, strava_error = load_strava_data()
# ============================================================
def load_strava_data():
    token = st.session_state.get("strava_token")
    if not token:
        return None, [], NEEDS_REAUTH

    # Ask Strava for up to 30 recent activities using our helper function.
    # "athlete/activities" is the API endpoint for ride/run/swim history.
    # The function returns (status_code, data).
    status, acts_data = _strava_get("athlete/activities", token, per_page=30)

    # Status 401 means "Unauthorized" — our token is expired or invalid.
    if status == 401:
        # Try getting a new token using the refresh token (automatic re-login).
        new_token = _refresh_strava_token()

        if new_token:
            # We got a fresh token — save it to session_state and try again.
            st.session_state.strava_token = new_token
            token = new_token

            # Retry the activities request with the fresh token.
            status, acts_data = _strava_get("athlete/activities", token, per_page=30)

            if status == 401:
                # Still getting 401 after a fresh token — this means the token
                # was created without the "activity:read_all" permission scope.
                # The user needs to go through a one-time re-authorization flow.
                # We return our special sentinel value NEEDS_REAUTH.
                return None, [], NEEDS_REAUTH
        else:
            # The refresh failed entirely — probably wrong credentials in secrets.toml.
            # Return a human-readable error message.
            return None, [], "Token refresh failed. Your session may have expired — please reconnect."

    # Status 0 is our own code for "no internet / couldn't reach Strava at all."
    if status == 0:
        return None, [], "Could not reach Strava. Check your internet connection and try again."

    # Any status other than 200 (success) that we haven't handled above.
    # Could be 500 (Strava server error), 429 (rate limit), etc.
    if status != 200:
        # f-string inserts the actual status code number into the error message.
        return None, [], f"Strava API returned HTTP {status}. Try refreshing in a moment."

    # Fetch the athlete's profile (contains their name, photo URL, etc.)
    # The _ (underscore) discards the status code — we don't need it here.
    _, athlete = _strava_get("athlete", token)

    # Filter the activities list to keep only cycling types.
    # This is a "list comprehension" — a compact way to build a new list:
    #   [expression  for item in list  if condition]
    # For each activity "a" in acts_data (or empty list if acts_data is None/falsy),
    # keep it only if a["type"] is in our CYCLING_TYPES set.
    # [:10] at the end takes only the first 10 results (Strava returns newest-first).
    rides_raw = [a for a in (acts_data or []) if a.get("type") in CYCLING_TYPES][:10]

    # If no cycling rides were found (user hasn't logged any yet):
    if not rides_raw:
        # Return the athlete profile, an empty list of rides, and no error.
        return athlete, [], None

    # Convert each raw Strava activity dictionary into a simpler, consistent format
    # that the rest of the app expects. This is another list comprehension.
    # For each activity "a" in rides_raw, build a new dictionary with our fields.
    past_rides = [{
        # a.get("name", "Ride") — get the ride name; use "Ride" as fallback if missing
        "name":          a.get("name", "Ride"),

        # Take only the first 10 characters of the ISO date string "2026-06-08T14:30:00Z"
        # The [:10] slice extracts just "2026-06-08"
        "date":          a["start_date_local"][:10],

        # Strava gives distance in metres. Divide by 1000 to get km.
        # round(..., 1) rounds to 1 decimal place, e.g. 42.3
        "distance_km":   round(a["distance"] / 1000, 1),

        # Strava gives moving time in seconds. Divide by 60 to get minutes.
        "duration_mins": round(a["moving_time"] / 60),

        # Strava gives speed in metres per second (m/s). Multiply by 3.6 to get km/h.
        # (1 m/s = 3.6 km/h because there are 3600 seconds in an hour and 1000 metres in a km)
        "avg_speed_kmh": round(a["average_speed"] * 3.6, 1),

        # Heart rate — some rides don't have HR data, so a.get() returns None.
        # "or 0" replaces None with 0. int() converts float to whole number.
        "avg_hr":        int(a.get("average_heartrate") or 0),
    } for a in rides_raw]

    # Strava returned rides newest-first, but our trend analysis needs oldest-first.
    # .reverse() flips the list in place (modifies it directly, returns nothing).
    past_rides.reverse()

    # Return the athlete profile, the processed rides list, and None (no error).
    return athlete, past_rides, None


# ============================================================
# SECTION 3: SESSION STATE INITIALIZATION
#
# Before drawing any UI, we make sure the "memory" (session_state) has
# default values for all the variables the app relies on.
# Without this, the first page load would crash because these keys don't exist yet.
#
# Pattern: "if key not in st.session_state" ensures we only set defaults once.
# After the first load, the user's actual choices are preserved in session_state.
# ============================================================

# tip_idx = which tip is currently being shown (0 = first tip in the list).
if "tip_idx" not in st.session_state:
    st.session_state.tip_idx = 0

if "calc_km" not in st.session_state:
    st.session_state.calc_km = None

if "calc_time" not in st.session_state:
    st.session_state.calc_time = None

# show_analysis = whether to display the ride analysis section.
# Starts as False — only becomes True after the user clicks "Calculate."
if "show_analysis" not in st.session_state:
    st.session_state.show_analysis = False

if "strava_token" not in st.session_state:
    st.session_state.strava_token = None

if "strava_refresh_token" not in st.session_state:
    st.session_state.strava_refresh_token = None

if "strava_athlete" not in st.session_state:
    st.session_state.strava_athlete = None


# ============================================================
# SECTION 3B: OAUTH CALLBACK HANDLER
#
# When Strava redirects back after authorization, the URL contains
# ?code=XXX&scope=... as query parameters. We detect them here,
# exchange the code for tokens, store in session_state, clear the URL,
# and rerun — after which the dashboard loads normally.
# ============================================================

_params = st.query_params

if "code" in _params and st.session_state.strava_token is None:
    with st.spinner("Connecting your Strava account…"):
        new_access, new_refresh, granted_scope = exchange_auth_code(_params["code"])
    if new_access and "activity:read" in granted_scope:
        st.session_state.strava_token = new_access
        st.session_state.strava_refresh_token = new_refresh
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Authorization failed or activity scope not granted. Please try again.")
        st.query_params.clear()
elif "error" in _params:
    st.warning("Strava authorization was cancelled.")
    st.query_params.clear()


# ============================================================
# SECTION 4: LOAD STRAVA DATA
#
# Now that the app is set up, we fetch real data from Strava.
# This runs every time the page loads or refreshes.
# The "with st.spinner(...)" block shows a loading animation while it runs.
# ============================================================

# st.spinner() displays a spinning loading indicator with custom text.
# The "with" keyword means: show the spinner while the indented code is running,
# then hide it when done.
with st.spinner("Fetching your latest rides from Strava…"):
    # Call our data-loading function and unpack its 3 return values.
    # athlete = the user's Strava profile dictionary (name, etc.)
    # past_rides = list of processed ride dictionaries
    # strava_error = None if all went well, or an error string if something failed
    athlete, past_rides, strava_error = load_strava_data()

# Check if we actually got any rides back.
# len() counts how many items are in a list.
# "> 0" means "more than zero."
# The result (True or False) is stored in has_rides for use throughout the app.
has_rides = len(past_rides) > 0


# ============================================================
# SECTION 4A: LOGIN GATE
#
# If load_strava_data() returned NEEDS_REAUTH, the user has no valid
# Strava token in their session. Show a login page and stop rendering
# the dashboard until they connect their account.
# ============================================================

if strava_error == NEEDS_REAUTH:
    creds = st.secrets["strava"]
    auth_url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
        "client_id":       creds["client_id"],
        "response_type":   "code",
        "redirect_uri":    REDIRECT_URI,
        "approval_prompt": "auto",
        "scope":           "activity:read_all",
    })
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("🚴 Cycling Dashboard")
        st.markdown("### Connect your Strava account to get started")
        st.markdown(
            "See your ride history, hydration targets, and training insights — "
            "personalised to your data."
        )
        st.link_button("🔗 Connect with Strava", url=auth_url, use_container_width=True, type="primary")
        st.caption("You'll be redirected to Strava to authorise, then returned here automatically.")
    st.stop()


weight_kg = 75


# ============================================================
# SECTION 6: RIDE CALCULATIONS
# Only runs after the user has submitted distance + time via the form.
# ============================================================

if st.session_state.calc_km is not None and st.session_state.calc_time is not None:
    target_km        = st.session_state.calc_km
    target_time_mins = st.session_state.calc_time
    target_speed_kmh = target_km / (target_time_mins / 60)
    duration_hours   = target_time_mins / 60

    if target_speed_kmh < 20:
        intensity_multiplier = 0.8
        intensity_label      = "🟢 Low"
    elif target_speed_kmh <= 26:
        intensity_multiplier = 1.0
        intensity_label      = "🟡 Moderate"
    else:
        intensity_multiplier = 1.2
        intensity_label      = "🔴 High"

    pre_ride_ml    = weight_kg * 6
    water_per_hour = 500 * intensity_multiplier
    active_ml      = water_per_hour * duration_hours
    total_ml       = pre_ride_ml + active_ml

    if duration_hours < 1:
        carb_pre_g       = round(weight_kg * 1.5)
        carb_pre_timing  = "1–2 hours before"
        carb_during_g    = 0
        carb_during_note = "Water only — short ride needs no solid fuel"
        carb_ratio_used  = 1.5
        carb_rate_used   = 0
    elif duration_hours < 1.5:
        carb_pre_g       = round(weight_kg * 2.0)
        carb_pre_timing  = "2–3 hours before"
        carb_during_g    = round(30 * duration_hours)
        carb_during_note = "~30 g/hr (one energy gel or a banana per hour)"
        carb_ratio_used  = 2.0
        carb_rate_used   = 30
    else:
        carb_pre_g       = round(weight_kg * 3.0)
        carb_pre_timing  = "3–4 hours before"
        carb_during_g    = round(60 * duration_hours)
        carb_during_note = "~60 g/hr (two gels or an energy bar + gel each hour)"
        carb_ratio_used  = 3.0
        carb_rate_used   = 60

    carb_post_g    = round(weight_kg * 1.2)
    protein_post_g = round(weight_kg * 0.4)
else:
    target_km = target_time_mins = target_speed_kmh = duration_hours = None
    intensity_multiplier = intensity_label = None
    pre_ride_ml = water_per_hour = active_ml = total_ml = None
    carb_pre_g = carb_pre_timing = carb_during_g = carb_during_note = None
    carb_ratio_used = carb_rate_used = carb_post_g = protein_post_g = None


# ============================================================
# SECTION 7: SPEED PREDICTION FROM STRAVA HISTORY
#
# If the user has Strava ride data, we analyse their past speeds to:
#   1. Calculate their historical average speed
#   2. Detect whether their speed is improving or declining (trend)
#   3. Suggest a target speed for the next ride (slightly above their average)
#
# This block only runs when has_rides is True (we have actual data to work with).
# ============================================================

if has_rides:
    # Convert the list of ride dictionaries into a pandas DataFrame (table).
    # A DataFrame is like a spreadsheet: rows are rides, columns are fields.
    rides_raw_df   = pd.DataFrame(past_rides)

    # Count how many rides we have total.
    last_n         = len(rides_raw_df)

    # .tail(10) returns the last 10 rows of the DataFrame (most recent 10 rides).
    # Since we reversed the list earlier, the last rows are the most recent.
    last_10_df     = rides_raw_df.tail(10)

    # Calculate the average speed across those last 10 rides.
    # ["avg_speed_kmh"] selects that column. .mean() computes the average.
    hist_avg_speed = last_10_df["avg_speed_kmh"].mean()

    # Split the rides into "older half" and "newer half" to detect a speed trend.
    # Integer division (//) rounds down: e.g. 7 // 2 = 3 (not 3.5).
    half = last_n // 2

    # We need at least 4 rides to have a meaningful trend comparison.
    if last_n >= 4:
        # .head(half) returns the first "half" rows (the older rides).
        older_avg   = last_10_df.head(half)["avg_speed_kmh"].mean()

        # .tail(last_n - half) returns the remaining rows (the newer rides).
        # last_n - half handles odd numbers correctly (e.g. if last_n=7, half=3, newer gets 4 rides).
        newer_avg   = last_10_df.tail(last_n - half)["avg_speed_kmh"].mean()

        # Trend = difference between newer average and older average.
        # Positive number = getting faster. Negative number = getting slower.
        speed_trend = newer_avg - older_avg
    else:
        # Not enough rides for a trend — set to 0 (neutral).
        speed_trend = 0.0

    suggested_speed    = hist_avg_speed * 1.02
    suggested_time_min = (target_km / suggested_speed) * 60 if target_km is not None else None


# ============================================================
# SECTION 8: PERSONALIZED WELCOME HEADER
#
# Shows "Good morning/afternoon/evening/night, [Name]!" based on the time of day,
# and a summary of the user's last Strava ride.
# ============================================================

# datetime.now() gets the current date and time on the server.
# .hour extracts just the hour as a number (0–23, i.e. 24-hour clock).
hour_of_day = datetime.now().hour

# Pick a greeting based on the hour.
# 5–11 = morning, 12–16 = afternoon, 17–20 = evening, 21–4 = night.
if 5 <= hour_of_day < 12:
    greeting = "Good morning"
elif 12 <= hour_of_day < 17:
    greeting = "Good afternoon"
elif 17 <= hour_of_day < 21:
    greeting = "Good evening"
else:
    greeting = "Good night"

rider_name = athlete.get("firstname", "Cyclist") if athlete else "Cyclist"

_title_col, _btns_col = st.columns([10, 1])
with _title_col:
    st.title(f"🚴 {greeting}, {rider_name}!")
with _btns_col:
    st.write("")
    if st.button("🔄", help="Refresh from Strava", use_container_width=True):
        _strava_get.clear()
        st.rerun()
    if st.button("🔌", help="Disconnect Strava", use_container_width=True):
        st.session_state.strava_token = None
        st.session_state.strava_refresh_token = None
        st.session_state.strava_athlete = None
        _strava_get.clear()
        st.rerun()

# Show different content below the title depending on the connection status.
if strava_error:
    # Something went wrong with Strava — show a red error banner.
    st.error(f"Strava connection issue: {strava_error}")

elif has_rides:
    # We have rides! Show info about the most recent one.
    # past_rides[-1] means "the last item in the list" (newest ride, since we reversed earlier).
    last_ride      = past_rides[-1]

    # Parse the date string "2026-06-08" into a real Python date object
    # so we can do date arithmetic (subtraction) on it.
    # "%Y-%m-%d" is the format pattern: year-month-day.
    last_ride_date = datetime.strptime(last_ride["date"], "%Y-%m-%d").date()

    # Calculate how many days ago the last ride was.
    # date.today() gets today's date. Subtracting two dates gives a timedelta object.
    # .days extracts the number of days from that timedelta.
    days_since     = (date.today() - last_ride_date).days

    # Pick a motivational message based on how long ago the last ride was.
    if days_since == 0:
        recency_msg = "You rode **today** — incredible consistency! 🔥"
    elif days_since == 1:
        recency_msg = "Last ride was **yesterday** — time to clip back in!"
    else:
        # The f-string inserts the actual number of days into the message.
        recency_msg = f"It's been **{days_since} days** since your last ride. The bike is waiting! 🚴"

    # Render the ride summary as markdown text.
    # &nbsp; is an HTML non-breaking space — adds a small gap between the ride info and recency message.
    st.markdown(
        f"Last Strava ride: **{last_ride['name']}** · {last_ride['distance_km']} km "
        f"at {last_ride['avg_speed_kmh']} km/h on {last_ride['date']}. &nbsp; {recency_msg}"
    )

else:
    # Strava connected fine but no cycling rides found yet.
    st.markdown("No cycling rides found on Strava yet. Log a ride and come back!")

# st.divider() draws a horizontal line across the page to separate sections.
st.divider()

_tips_col, _analysis_col = st.columns([1, 2], gap="large")

# ============================================================
# SECTION 9: DAILY KNOWLEDGE — CYCLING TIPS (left column)
# ============================================================

with _tips_col:
    st.subheader("💡 Daily Knowledge")

    _filtered_tips = cycling_tips_categorized
    _safe_idx = st.session_state.tip_idx % len(_filtered_tips)
    _tip_data = _filtered_tips[_safe_idx]

    st.info(f"**[{_tip_data['category']}]** {_tip_data['tip']}")
    st.caption(f"Tip {_safe_idx + 1} of {len(_filtered_tips)}")

    if st.button("🔄 Next Tip", use_container_width=True):
        st.session_state.tip_idx = (st.session_state.tip_idx + 1) % len(_filtered_tips)
        st.rerun()


# ============================================================
# SECTION 10: NEXT RIDE ANALYSIS (right column)
# ============================================================

with _analysis_col:
    st.header("📊 Next Ride Analysis")

    st.subheader("🎯 Plan Your Next Ride")
    st.caption("Speed and intensity are calculated automatically from distance and time.")

    _plan_col1, _plan_col2 = st.columns(2)

    with _plan_col1:
        target_km_input = st.number_input(
            "Target Distance (km)",
            min_value=5.0, max_value=300.0,
            value=st.session_state.calc_km,
            placeholder="e.g. 40",
            step=0.5,
        )

    with _plan_col2:
        target_time_input = st.number_input(
            "Target Time (minutes)",
            min_value=15, max_value=600,
            value=st.session_state.calc_time,
            placeholder="e.g. 90",
            step=5,
        )

    if st.button("🚀 Calculate", type="primary", use_container_width=True):
        if target_km_input is None or target_time_input is None:
            st.error("Please enter both a target distance and time.")
        else:
            st.session_state.calc_km   = target_km_input
            st.session_state.calc_time = target_time_input
            st.session_state.show_analysis = True
            st.rerun()

    if st.session_state.show_analysis:
        st.markdown("""
        <div style="background:#e8f4fd; border-left:4px solid #1a73e8;
                    padding:10px 16px; border-radius:6px; margin:16px 0 4px 0;">
            ✅ <strong>Results for your planned ride</strong>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("📈 Ride Analysis")
            st.caption(
                f"Plan: **{target_km} km** in **{target_time_mins} min** "
                f"→ implied speed **{target_speed_kmh:.1f} km/h**"
            )

            _i1, _i2 = st.columns([1, 3])
            with _i1:
                st.metric("Predicted Intensity", intensity_label)
            with _i2:
                st.write("")
                st.markdown(
                    f"Targeting **{target_km} km** in **{target_time_mins} minutes** implies an average speed of "
                    f"**{target_speed_kmh:.1f} km/h**, classified as **{intensity_label}** intensity "
                    f"(hydration multiplier: **{intensity_multiplier}×**)."
                )

            st.divider()
            st.subheader("🧠 Smart Training Insights")

            if not has_rides:
                st.info("Log some rides on Strava and your speed targets will appear here automatically.")
            else:
                st.caption(
                    f"Speed targets derived from your last **{last_n} Strava rides** — "
                    "updates automatically as new rides are recorded."
                )

                _s1, _s2, _s3 = st.columns(3)

                with _s1:
                    _trend_label = (
                        f"+{speed_trend:.1f} km/h improving" if speed_trend > 0
                        else f"{speed_trend:.1f} km/h declining"
                    )
                    st.metric(
                        "Your Recent Avg Speed",
                        f"{hist_avg_speed:.1f} km/h",
                        delta=_trend_label if last_n >= 4 else None,
                        help="Mean of your last 10 Strava rides."
                    )

                with _s2:
                    st.metric(
                        "Suggested Target Speed",
                        f"{suggested_speed:.1f} km/h",
                        delta=f"+{suggested_speed - hist_avg_speed:.2f} km/h vs your average",
                        help="2% above your historical average — the standard progressive overload step."
                    )

                with _s3:
                    st.metric(
                        f"Suggested Time for {target_km:.0f} km",
                        f"{suggested_time_min:.0f} min",
                        help=f"Time to cover {target_km} km at {suggested_speed:.1f} km/h."
                    )

                if target_speed_kmh > suggested_speed * 1.05:
                    st.warning(
                        f"⚡ Your target ({target_speed_kmh:.1f} km/h) is **more than 5% above your Strava average**. "
                        "Ambitious — ensure you're well-rested and carb-loaded!"
                    )
                elif target_speed_kmh < hist_avg_speed * 0.90:
                    st.info(
                        f"🧘 Your target ({target_speed_kmh:.1f} km/h) is below your usual pace — "
                        "looks like a **recovery or easy ride**. A smart choice."
                    )
                else:
                    st.success(
                        f"✅ Your target ({target_speed_kmh:.1f} km/h) sits well within your Strava range — "
                        "a solid, achievable goal!"
                    )

            st.divider()
            st.subheader("💧 Hydration & Fuel Guide")

            st.markdown("**Hydration Plan**")
            _h1, _h2, _h3, _h4 = st.columns(4)
            with _h1:
                st.metric("Pre-Ride", f"{pre_ride_ml:.0f} ml", help="Drink in the 2 hours before you start.")
            with _h2:
                st.metric("During (per hour)", f"{water_per_hour:.0f} ml/hr", help="Sip steadily each hour on the bike.")
            with _h3:
                st.metric("During (total)", f"{active_ml:.0f} ml", help="Total water target across the full ride.")
            with _h4:
                st.metric("Grand Total", f"{total_ml:.0f} ml", help="Pre-ride + full-ride water combined.")

            st.markdown("**Carb Fuel Guide**")
            _c1, _c2, _c3 = st.columns(3)
            with _c1:
                st.markdown("**Pre-Ride**")
                st.metric(f"Carbs ({carb_pre_timing})", f"{carb_pre_g} g")
                st.caption("e.g. oats, rice, pasta, banana, toast with honey")
            with _c2:
                st.markdown("**During Ride**")
                st.metric("Carbs (total)", f"{carb_during_g} g")
                st.caption(carb_during_note)
            with _c3:
                st.markdown("**Post-Ride** *(within 30 min)*")
                st.metric("Carbs", f"{carb_post_g} g")
                st.metric("Protein", f"{protein_post_g} g")
                st.caption("e.g. chocolate milk, Greek yogurt + fruit, recovery shake")

            with st.expander("📐 See Full Calculation Breakdown"):
                st.write(f"""
**Your Inputs:**
- Target: **{target_km} km** in **{target_time_mins} min** ({duration_hours:.1f} hrs)
- Derived speed: **{target_speed_kmh:.1f} km/h** → Intensity: **{intensity_label}** (×{intensity_multiplier})

---

**Hydration Formulas:**
- Pre-ride: `{weight_kg} × 6 = {pre_ride_ml:.0f} ml`
- During (per hour): `500 ml × {intensity_multiplier} = {water_per_hour:.0f} ml/hr`
- During (total): `{water_per_hour:.0f} × {duration_hours:.1f} hrs = {active_ml:.0f} ml`
- Grand total: `{pre_ride_ml:.0f} + {active_ml:.0f} = {total_ml:.0f} ml`

**Carb Formulas:**
- Pre-ride: `{weight_kg} kg × {carb_ratio_used} g/kg = {carb_pre_g} g`
- During: `{carb_rate_used} g/hr × {duration_hours:.1f} hrs = {carb_during_g} g`
- Post-ride carbs: `{weight_kg} × 1.2 g/kg = {carb_post_g} g`
- Post-ride protein: `{weight_kg} × 0.4 g/kg = {protein_post_g} g`
                """)

st.divider()


# ============================================================
# SECTION 12: PAST RIDE LOG (live from Strava)
#
# Displays a colour-coded table of the user's recent Strava rides.
# pandas and its styling system are used to add background colours
# to the Intensity column based on each ride's speed.
# ============================================================

st.header("🗂️ Past Ride Log")

if not has_rides:
    # No rides yet — show a friendly placeholder message.
    st.info("Your Strava cycling activities will appear here once you have recorded some rides.")
else:
    # Show a caption explaining the colour coding.
    st.caption(
        f"Your last {len(past_rides)} Strava rides, most recent first. "
        "Intensity is colour-coded from average speed: 🟢 < 20 · 🟡 20–26 · 🔴 > 26 km/h."
    )

    # A small helper function to classify a speed value into an intensity label.
    # Functions can be defined anywhere in the file and called later.
    def classify_intensity(speed):
        if speed < 20:
            return "🟢 Low"
        elif speed <= 26:
            return "🟡 Moderate"
        else:
            return "🔴 High"

    # Convert past_rides (list of dicts) into a pandas DataFrame.
    # .iloc[::-1] reverses the row order — [::-1] is Python slice notation for "reverse."
    # .reset_index(drop=True) renumbers the rows from 0 after reversing (so row 0 = newest).
    rides_display = pd.DataFrame(past_rides).iloc[::-1].reset_index(drop=True)

    # Add a new "Intensity" column by applying our classify_intensity function
    # to every value in the "avg_speed_kmh" column.
    # .apply() runs the function once for each row and collects the results.
    rides_display["Intensity"] = rides_display["avg_speed_kmh"].apply(classify_intensity)

    # Rename the column headers to human-friendly display names.
    # .rename(columns={...}) takes a dictionary mapping old names → new names.
    rides_display = rides_display.rename(columns={
        "name":          "Ride Name",
        "date":          "Date",
        "distance_km":   "Distance (km)",
        "duration_mins": "Duration (mins)",
        "avg_speed_kmh": "Avg Speed (km/h)",
    })

    # Select only the columns we want to show (in the desired display order).
    # The "avg_hr" column is silently dropped by not including it here.
    rides_display = rides_display[[
        "Ride Name", "Date", "Distance (km)",
        "Duration (mins)", "Avg Speed (km/h)", "Intensity",
    ]]

    # A helper function that returns a CSS style string based on the intensity value.
    # CSS (Cascading Style Sheets) is the language that controls visual appearance on web pages.
    # background-color: the cell background colour (hex colour codes like #c6efce = light green)
    # color: the text colour inside the cell
    # font-weight: bold makes the text bold
    def style_intensity(val):
        if "Low" in str(val):
            return "background-color: #c6efce; color: #276221; font-weight: bold"   # Green
        elif "Moderate" in str(val):
            return "background-color: #ffeb9c; color: #9c6500; font-weight: bold"   # Yellow
        elif "High" in str(val):
            return "background-color: #ffc7ce; color: #9c0006; font-weight: bold"   # Red
        return ""  # No styling for cells that don't match any category

    # Apply the cell styling to the Intensity column.
    # Different versions of pandas use different method names for this:
    # Newer versions use .map(), older versions use .applymap().
    # The try/except handles whichever version is installed.
    try:
        # Newer pandas (>= 2.1): use .map() with a subset to target only the Intensity column.
        styled_df = rides_display.style.map(style_intensity, subset=["Intensity"])
    except AttributeError:
        # Older pandas: fall back to .applymap() with the same arguments.
        styled_df = rides_display.style.applymap(style_intensity, subset=["Intensity"])

    # Display the styled table on the page.
    # use_container_width=True stretches it to fill the available width.
    # hide_index=True hides the row numbers (0, 1, 2...) on the left.
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


# ============================================================
# SECTION 13: FOOTER
#
# A small credit line centred at the bottom of the page.
# ============================================================

st.divider()

# Create three equal columns. The _ (underscore) variables discard the outer two —
# we only care about the middle column (footer_center) for centring.
_, footer_center, _ = st.columns([1, 1, 1])

with footer_center:
    # st.caption() renders small, grey, secondary text — perfect for a footer credit.
    st.caption("Built with Python & Streamlit · Powered by Strava · 2026")
