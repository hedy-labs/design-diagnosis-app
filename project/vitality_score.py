"""
Visual Vitality Score Engine — v0.7
------------------------------------
MVP: Link-to-Report for Airbnb hosts.

Philosophy: "Would you live here? Your guests have to."

What's new in v0.7:
  - Two-step verification: Step 1 = Visual Inventory (what the AI sees),
    Step 2 = Stager's Logic applied to that inventory.
    Images are only processed ONCE (Step 1). Step 2 is text-only = faster + cheaper.
  - Listing type weighting: scoring adapts to Urban Studio / Resort / City Apartment / Family Home
  - 'Why' factor: every shopping list item includes a design justification
  - Smart hero selection: auto-picks the 5 most important rooms by filename keywords;
    use --all-images to override

Previous features retained:
  - Image optimisation (Pillow, max 1500px)
  - Exponential backoff on 429 rate limit errors
  - Safety timeout (30 seconds)
  - Safety cap (max 10 images)
  - Competitor data placeholder
  - Monetized shopping list (Item / Cost / Online|Near Me / Link / Why)
  - Reality Gap Score
  - URL-ready architecture (Airbnb scraper swap point)

Usage:
    python vitality_score.py \\
        --images bedroom.jpg kitchen.jpg bathroom.jpg living.jpg dining.jpg \\
        --location "Barcelona, Spain" \\
        --budget 500 \\
        --currency EUR \\
        --listing-type urban_studio \\
        --shopping-preference both \\
        --corrections "Sofa is light blue velvet" \\
        --guest-report "Mouldy shower curtain on arrival" \\
        --competitor-avg-score 61 \\
        --all-images
"""

import argparse
import base64
import io
import json
import signal
import time
from pathlib import Path

from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────────
# SAFETY CONSTANTS
# ─────────────────────────────────────────────────────────────
MAX_IMAGES      = 10
HERO_LIMIT      = 5       # smart selection: max hero rooms sent to API
MAX_IMAGE_WIDTH = 1500    # px
PROCESS_TIMEOUT = 60      # seconds (increased to accommodate 2-step flow)
MAX_RETRIES     = 4
BACKOFF_BASE    = 5       # seconds (doubles: 5, 10, 20, 40)

# Hero room priority — matched against filename keywords (order = priority)
HERO_KEYWORDS = [
    "bedroom", "bed",
    "living", "lounge", "main",
    "bathroom", "bath",
    "kitchen",
    "dining",
]

# ─────────────────────────────────────────────────────────────
# SHOPPING PREFERENCE
# Controls whether the report generates online links, local store
# suggestions, or both. The host chooses at run time.
# ─────────────────────────────────────────────────────────────
SHOPPING_PREFERENCES = {
    "online":   "Online only — provide purchase URLs for each item.",
    "in_store": "In-store only — provide local store names and areas for each item.",
    "both":     "Provide both an online purchase URL and a local store suggestion for each item.",
    "curated":  "Use the Curated Vendor List only — match items to the pre-approved vendors below.",
}

# ─────────────────────────────────────────────────────────────
# CURATED VENDOR LIST
# Pre-approved, globally relevant vendors.
# Hosts can request items sourced from this list only.
# Future: this list will be editable per-user in the web UI.
# ─────────────────────────────────────────────────────────────
CURATED_VENDORS = {
    "global": [
        {"name": "IKEA",    "url": "https://www.ikea.com",    "notes": "Furniture, rugs, lighting, storage"},
        {"name": "Amazon",  "url": "https://www.amazon.com",  "notes": "General homeware, accessories"},
        {"name": "Wayfair", "url": "https://www.wayfair.com", "notes": "Furniture and décor, ships internationally"},
    ],
    "SE Asia": [
        {"name": "Shopee",  "url": "https://shopee.com",      "notes": "General homeware, ships across SE Asia"},
        {"name": "Lazada",  "url": "https://www.lazada.com",  "notes": "General homeware, ships across SE Asia"},
        {"name": "MR DIY",  "url": "https://www.mrdiy.com",   "notes": "Hardware, hooks, organisers — Malaysia"},
    ],
    "Europe": [
        {"name": "Zara Home", "url": "https://www.zarahome.com", "notes": "Textiles, cushions, bedding"},
        {"name": "H&M Home",  "url": "https://www.hm.com/home",  "notes": "Affordable décor and textiles"},
    ],
    "North America": [
        {"name": "Target",    "url": "https://www.target.com",   "notes": "Affordable homeware"},
        {"name": "Crate & Barrel", "url": "https://www.crateandbarrel.com", "notes": "Mid-range furniture and décor"},
    ],
    "Australia": [
        {"name": "Kmart AU",  "url": "https://www.kmart.com.au", "notes": "Affordable homeware"},
        {"name": "Temple & Webster", "url": "https://www.templeandwebster.com.au", "notes": "Furniture and décor"},
    ],
}

# ─────────────────────────────────────────────────────────────
# HOST GOALS
# Re-weights recommendations based on the host's primary objective.
# ─────────────────────────────────────────────────────────────
HOST_GOALS = {
    "rate": {
        "label": "Increase Nightly Rate",
        "priority_note": """
The host's primary goal is to INCREASE THEIR NIGHTLY RATE.
Prioritise recommendations that justify a premium price point:
- Aesthetic upgrades that signal luxury or intentional design (hero photos, colour coherence)
- Items that close the gap between this listing and higher-priced competitors
- Staging improvements that elevate the perceived value in listing photos
- Lead the report summary with: what is preventing this listing from commanding a higher rate?
Lead every shopping list item with its impact on perceived value, not just function.
""",
    },
    "vacancy": {
        "label": "Reduce Vacancy / Increase Bookings",
        "priority_note": """
The host's primary goal is to REDUCE VACANCY and increase booking frequency.
Prioritise recommendations that improve scroll-through and booking conversion:
- First-impression score: does the hero/cover photo make a guest stop scrolling?
- Missing photos that are creating doubt (bathroom, dining, kitchen)
- Competitive positioning: is this listing above or below the market average?
- Staging integrity: honest, appealing presentation that builds trust quickly
Lead the report summary with: what is preventing guests from clicking 'Book Now'?
Lead every shopping list item with its impact on listing appeal and click-through rate.
""",
    },
    "rating": {
        "label": "Improve Guest Ratings",
        "priority_note": """
The host's primary goal is to IMPROVE THEIR OVERALL GUEST RATING.
Prioritise recommendations that close the gap between expectation and reality:
- Functional Anchors: missing items that guests complain about (no bedside table, no workspace)
- Reality Gap: anything that misleads guests vs. what they find on arrival
- Show It List: amenities that exist but aren't shown — preventing trust before booking
- Hidden friction: non-visual items (linen quality, shower storage, entry hooks)
Lead the report summary with: what are guests most likely complaining about right now?
Lead every shopping list item with its direct impact on guest satisfaction and review scores.
""",
    },
    "all": {
        "label": "All Goals (Balanced)",
        "priority_note": """
The host wants to improve across all three dimensions: nightly rate, vacancy, and ratings.
Balance recommendations evenly across aesthetic premium, listing appeal, and guest satisfaction.
Group the shopping list into three clear sections: Rate Boosters / Booking Drivers / Review Protectors.
""",
    },
}
DEFAULT_GOAL = "all"

# ─────────────────────────────────────────────────────────────
# LISTING TYPE DEFINITIONS
# Each type adjusts scoring weights and recommendation language.
# ─────────────────────────────────────────────────────────────
LISTING_TYPES = {
    "urban_studio": {
        "label": "Urban Studio",
        "weight_notes": """
- Functional Anchors are CRITICAL (guests live/work/sleep in one room).
  Workspace, zone definition, and entry storage carry extra weight.
- Colour Coherence is important — a small space is unforgiving of clashing colours.
- Clutter & Space Flow: heavily penalise anything that makes the space feel smaller.
- Staging Integrity: guests scrutinise studio photos closely; every item must be honest.
""",
    },
    "resort": {
        "label": "Resort / Holiday Villa",
        "weight_notes": """
- Colour Coherence is CRITICAL — resort guests expect a curated, immersive aesthetic.
  Tropical, coastal, or local design language should be intentional and consistent.
- Lighting Quality carries extra weight — ambience is a core part of the resort experience.
- Functional Anchors: outdoor seating, pool/garden visibility, and communal areas
  matter as much as bedroom anchors.
- Staging Integrity: welcome amenities (fruit, flowers, towel art) are EXPECTED at resort
  level — but only photograph what every guest actually receives.
""",
    },
    "city_apartment": {
        "label": "City Apartment",
        "weight_notes": """
- Functional Anchors: workspace is essential — city travellers are often bleisure guests.
- Staging Integrity: honest, professional presentation. No over-staging.
- Clutter & Space Flow: CRITICAL. Apply 'Strategic Urban Clarity' principles:
    * TV should be wall-mounted wherever possible to reclaim floor space occupied by console.
    * Sofa should be reoriented so its BACK faces the bed zone, creating a visual barrier
      between living and sleeping areas — this is the single highest-impact spatial move
      in a combined living/sleeping studio.
    * A console table behind the sofa (facing away from the bed) reinforces the division.
    * Flag any TV console as a 'floor space reclaim opportunity' in the recommendations.
    * Flag any layout where bed and sofa face the same direction with no visual divider.
- Colour Coherence: neutral, broadly appealing palette preferred over bold choices.
""",
    },
    "family_home": {
        "label": "Family Home",
        "weight_notes": """
- Functional Anchors: multiple sleeping configurations, dining for 4+, and storage
  for family gear (pram, luggage, beach bags) carry extra weight.
- Clutter & Space Flow: safety and clear floor space are paramount.
- Staging Integrity: family listings must be especially honest — a broken chair or
  unsafe furniture is a liability, not just an aesthetic issue.
- Colour Coherence: warm, welcoming palette preferred.
""",
    },
}
DEFAULT_LISTING_TYPE = "city_apartment"


# ─────────────────────────────────────────────────────────────
# SAFETY TIMEOUT
# ─────────────────────────────────────────────────────────────

def _timeout_handler(signum, frame):
    raise TimeoutError(
        f"Safety timeout: process exceeded {PROCESS_TIMEOUT}s. "
        "Try with fewer or smaller images."
    )

signal.signal(signal.SIGALRM, _timeout_handler)


# ─────────────────────────────────────────────────────────────
# SMART HERO SELECTION
# Picks the HERO_LIMIT most important rooms by filename keyword.
# Falls back to first HERO_LIMIT images if no keywords match.
# ─────────────────────────────────────────────────────────────

def select_hero_images(image_paths: list[str]) -> tuple[list[str], list[str]]:
    """
    Returns (selected, skipped) — up to HERO_LIMIT hero room images.

    Priority order follows HERO_KEYWORDS. If multiple images match the
    same keyword (e.g. bedroom_1, bedroom_2), only the first is selected.
    """
    selected   = []
    used_keys  = set()
    remaining  = list(image_paths)

    for keyword in HERO_KEYWORDS:
        if len(selected) >= HERO_LIMIT:
            break
        for path in remaining:
            if keyword in Path(path).stem.lower() and keyword not in used_keys:
                selected.append(path)
                used_keys.add(keyword)
                remaining.remove(path)
                break

    # Fill remaining slots with whatever's left (in order provided)
    while len(selected) < HERO_LIMIT and remaining:
        selected.append(remaining.pop(0))

    skipped = [p for p in image_paths if p not in selected]
    return selected, skipped


# ─────────────────────────────────────────────────────────────
# PHOTO SOURCE ABSTRACTION
# TODAY:  local file list
# FUTURE: Airbnb URL scraper — swap point below
# ─────────────────────────────────────────────────────────────

def get_photos_from_source(source) -> list[str]:
    """
    TODAY:   source = list of local file paths.
    FUTURE:  source = Airbnb listing URL string.
             Uncomment the scraper block when ready.
    """
    if isinstance(source, str) and source.startswith("https://"):
        # ── FUTURE: Airbnb URL scraper ──────────────────────────
        # from scraper import fetch_airbnb_photos
        # photos = fetch_airbnb_photos(source)
        # if len(photos) > MAX_IMAGES:
        #     photos = photos[:MAX_IMAGES]
        # return photos
        # ────────────────────────────────────────────────────────
        raise NotImplementedError(
            "Airbnb URL scraping is not yet implemented. "
            "Pass local image file paths for now."
        )

    if len(source) > MAX_IMAGES:
        raise ValueError(
            f"Safety limit: maximum {MAX_IMAGES} images per run. "
            f"You provided {len(source)}. Use --all-images to bypass smart selection, "
            f"or let smart selection pick the {HERO_LIMIT} hero rooms automatically."
        )

    return source


# ─────────────────────────────────────────────────────────────
# IMAGE OPTIMISATION
# ─────────────────────────────────────────────────────────────

def optimise_and_encode(image_path: str) -> tuple[str, str]:
    """Resize to max MAX_IMAGE_WIDTH px, return (base64, mime_type)."""
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > MAX_IMAGE_WIDTH:
            ratio      = MAX_IMAGE_WIDTH / img.width
            new_height = int(img.height * ratio)
            img        = img.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode("utf-8")
    return b64, "image/jpeg"


# ─────────────────────────────────────────────────────────────
# STEP 1 PROMPT: VISUAL INVENTORY
# Ask the model to describe what it sees objectively — no scoring yet.
# This separates observation from judgement and improves accuracy.
# ─────────────────────────────────────────────────────────────

INVENTORY_PROMPT = """
You are conducting a Visual Inventory of an Airbnb listing.
Your task is ONLY to document what you see. Do not score or judge yet.

For each photo, document:
- Room type (bedroom, bathroom, kitchen, living room, etc.)
- Every piece of furniture visible (name, colour, approximate size/style)
- Lighting sources present (natural light, overhead, lamps, etc.)
- Textiles (bedding colour/condition, curtains, rugs, throws, cushions)
- Staging items (food, drink, flowers, props on surfaces)
- Anything missing that would normally be expected in this room type
- Condition notes (anything that looks worn, broken, mismatched, or out of place)

Return ONLY valid JSON in this format:

{
  "rooms": [
    {
      "room_type": "<bedroom|bathroom|kitchen|living_room|dining|entry|other>",
      "furniture": ["<item: colour, style>", ...],
      "lighting": ["<source description>", ...],
      "textiles": ["<item: colour, condition>", ...],
      "staging_props": ["<item>", ...],
      "missing_items": ["<expected item not present>", ...],
      "condition_notes": ["<observation>", ...]
    }
  ],
  "overall_palette": "<brief description of colour tones across all photos>",
  "photo_count": <int>,
  "listing_type_guess": "<urban_studio|resort|city_apartment|family_home>"
}
"""


# ─────────────────────────────────────────────────────────────
# STEP 2 PROMPT: STAGER'S LOGIC SCORING
# Takes the Visual Inventory as text input — no images needed.
# Applies scoring, recommendations, and shopping list.
# ─────────────────────────────────────────────────────────────

def build_scoring_prompt(
    inventory: dict,
    location: str,
    budget: float,
    currency: str,
    listing_type: str,
    corrections: str = "",
    guest_report: str = "",
    competitor_avg_score: float | None = None,
    shopping_preference: str = "both",
    goal: str = DEFAULT_GOAL
) -> str:

    lt       = LISTING_TYPES.get(listing_type, LISTING_TYPES[DEFAULT_LISTING_TYPE])
    lt_label = lt["label"]
    lt_notes = lt["weight_notes"]
    goal_obj  = HOST_GOALS.get(goal, HOST_GOALS[DEFAULT_GOAL])
    goal_label = goal_obj["label"]
    goal_note  = goal_obj["priority_note"]

    corrections_block = f"""
## Host Corrections
Treat these as ground truth — override visual analysis where they conflict:
{corrections}
""" if corrections else ""

    reality_gap_block = f"""
## Guest Reality Report
First-hand account of actual conditions on arrival. Use to calculate Reality Gap Score:
{guest_report}
""" if guest_report else ""

    competitor_block = f"""
## Market Context
Average Vitality Score of comparable listings in this area: {competitor_avg_score}/100
""" if competitor_avg_score is not None else """
## Market Context
No competitor data provided. Set market_position.competitor_avg_score to null.
"""

    # Shopping preference instruction
    shopping_preference_instruction = SHOPPING_PREFERENCES.get(
        shopping_preference, SHOPPING_PREFERENCES["both"]
    )

    # Build curated vendor string for the location
    import re
    location_lower = location.lower()
    region = "global"
    if any(x in location_lower for x in ["malaysia", "thailand", "singapore", "indonesia",
                                          "vietnam", "philippines", "kuala lumpur", "bangkok",
                                          "kl", "hua hin", "ampang"]):
        region = "SE Asia"
    elif any(x in location_lower for x in ["france", "spain", "italy", "germany", "uk",
                                            "london", "paris", "amsterdam", "barcelona"]):
        region = "Europe"
    elif any(x in location_lower for x in ["usa", "canada", "new york", "los angeles",
                                            "toronto", "chicago", "miami"]):
        region = "North America"
    elif any(x in location_lower for x in ["australia", "sydney", "melbourne", "brisbane"]):
        region = "Australia"

    vendors = CURATED_VENDORS["global"] + CURATED_VENDORS.get(region, [])
    curated_vendors_str = ", ".join(
        f"{v['name']} ({v['url']})" for v in vendors
    )

    return f"""
You are an expert Airbnb listing auditor applying the Stager's Logic scoring framework.

Core philosophy: "Would you live here? Your guests have to."

## Property Context
- Location: {location}
- Listing Type: {lt_label}
- Host's Primary Goal: {goal_label}
- Total upgrade budget: {currency} {budget:,.0f} (shopping list must not exceed this)
- Currency: {currency}
{corrections_block}{reality_gap_block}{competitor_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOST GOAL: {goal_label.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{goal_note}

## Visual Inventory (from Step 1 analysis)
{json.dumps(inventory, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LISTING TYPE SCORING WEIGHTS: {lt_label.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{lt_notes}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VITALITY SCORE DIMENSIONS (0–20 each = 100 total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Colour Coherence** (0–20)
   - Do all rooms share a cohesive palette?
   - Deduct for: clashing warm/cool tones with no unifying element.
   - Reward for: intentional, consistent palette.

2. **Lighting Quality** (0–20)
   - Multiple light sources present (ambient + task + accent)?
   - Deduct for: single harsh overhead, no bedside lamps, colour cast.

3. **Functional Anchors** (0–20)
   - Paired bedside tables + lamps, sofa side tables, adequate dining surface,
     dedicated workspace (desk + proper chair, NOT a vanity stool),
     entry storage (hooks, shoe rack, bench).
   - Heavy deduction for any missing anchor.

4. **Clutter & Space Flow** (0–20)
   - Clear floor space, furniture scaled to room, zones defined in open-plan spaces.

5. **Staging Integrity** (0–20)
   PHOTOGRAPH (neat): kitchen, bathroom (CRITICAL OMISSION if absent),
   dining (CRITICAL OMISSION if absent), wardrobe, washing machine.

   LIST IN AMENITIES ONLY (never photograph):
   vacuum, mop, iron, cleaning supplies.

   DEDUCT FOR: staging props not provided to guests, TV showing live content,
   mirror reflections revealing unstaged room, unmade beds or personal items.

   WALL ART: default = above bed headboard.
   Only suggest sofa wall art if solid wall clearly visible directly behind sofa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REALITY GAP SCORE (if guest report provided)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score each 0–10. Total max 80.
Categories: Mould & Hygiene | Plumbing Integrity | Pest Presence |
Electrical & Fixtures | Furniture Safety | Linen & Bedding Quality |
Props Fraud | Host Responsiveness
Severity: 0-10 minor | 11-25 moderate | 26-45 serious | 46+ fraudulent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHOPPING LIST RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is a GLOBAL app. The property is in {location}.
Recommend vendors that are available and relevant to that location.
Use globally recognised retailers where possible (IKEA, Amazon, Wayfair, Zara Home, H&M Home).
For local-specific stores, match to the region (SE Asia, Europe, North America, Australia, etc).

Shopping preference for this report: {shopping_preference_instruction}

Curated vendors available for this region: {curated_vendors_str}

- Every item MUST include a 'why' field: a plain-language design justification for the host.
  E.g.: "Paired bedside lamps create a hotel-standard sleep environment and make the bedroom
   the hero shot of your listing."
- Every item MUST include a 'show_it' boolean: true if the item already EXISTS at the property
  but is not visible in the listing photos (host just needs to photograph it), false if it needs
  to be purchased.
- Prefer warm-wood bedside tables when warm-wood TV console already present.
- Prioritise quick wins: lowest cost, highest visual/functional impact first.
- Total of items where show_it=false must not exceed {currency} {budget:,.0f}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT — valid JSON only, no prose
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "vitality_score": <int 0-100>,
  "grade": "<A/B/C/D/F>",
  "listing_type": "{listing_type}",
  "summary": "<2-3 sentence unified assessment>",
  "dimensions": {{
    "colour_coherence":   {{ "score": <int 0-20>, "notes": "<finding>" }},
    "lighting_quality":   {{ "score": <int 0-20>, "notes": "<finding>" }},
    "functional_anchors": {{ "score": <int 0-20>, "notes": "<finding>" }},
    "clutter_space_flow": {{ "score": <int 0-20>, "notes": "<finding>" }},
    "staging_integrity":  {{ "score": <int 0-20>, "notes": "<finding>" }}
  }},
  "critical_flags": ["<issue>", ...],
  "photo_actions": [
    {{
      "photo_subject": "<what the photo shows>",
      "action": "keep" | "restyle_before_reshoot" | "delete" | "add_to_amenities_list_only",
      "reason": "<explanation>"
    }}
  ],
  "reality_gap": {{
    "has_guest_report": <bool>,
    "total_score": <int 0-80 or null>,
    "severity": "none" | "minor" | "moderate" | "serious" | "fraudulent",
    "categories": {{
      "mould_hygiene":         {{ "score": <int 0-10>, "finding": "<reported>" }},
      "plumbing_integrity":    {{ "score": <int 0-10>, "finding": "<reported>" }},
      "pest_presence":         {{ "score": <int 0-10>, "finding": "<reported>" }},
      "electrical_fixtures":   {{ "score": <int 0-10>, "finding": "<reported>" }},
      "furniture_safety":      {{ "score": <int 0-10>, "finding": "<reported>" }},
      "linen_bedding_quality": {{ "score": <int 0-10>, "finding": "<reported>" }},
      "props_fraud":           {{ "score": <int 0-10>, "finding": "<reported>" }},
      "host_responsiveness":   {{ "score": <int 0-10>, "finding": "<reported>" }}
    }},
    "safety_alerts": ["<physical risk>", ...],
    "summary": "<Reality Gap verdict>"
  }},
  "market_position": {{
    "competitor_avg_score": <float or null>,
    "listing_vs_market": "above" | "at" | "below" | "unknown",
    "gap_to_market": <int or null>,
    "projected_score_after_fixes": <int 0-100>,
    "revenue_impact_note": "<brief estimate of booking/revenue impact>"
  }},
  "quick_wins": ["<fix>", ...],
  "show_it_list": [
    {{
      "item": "<item that exists but isn't shown in listing photos>",
      "action": "<exactly what photo to take / how to show it>",
      "impact": "<why showing this builds guest trust>"
    }}
  ],
  "shopping_list": [
    {{
      "item": "<product name>",
      "why": "<plain-language design justification for the host>",
      "reason": "<what functional/aesthetic gap it fixes>",
      "show_it": false,
      "sourcing": "online" | "near_me" | "both" | "curated",
      "purchase_link": "<primary URL>",
      "alternative_link": "<second option if sourcing=both, else null>",
      "estimated_cost_{currency.lower()}": <float>
    }}
  ],
  "shopping_list_total_{currency.lower()}": <float>
}}
"""


# ─────────────────────────────────────────────────────────────
# API CALL WITH EXPONENTIAL BACKOFF
# ─────────────────────────────────────────────────────────────

def call_api_with_backoff(
    messages: list,
    max_tokens: int = 3000,
    label: str = "API"
) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except RateLimitError:
            wait = BACKOFF_BASE * (2 ** attempt)
            if attempt < MAX_RETRIES - 1:
                print(f"  [{label}] Rate limit hit. Retrying in {wait}s "
                      f"(attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Rate limit persisted after {MAX_RETRIES} retries. "
                    "Please wait a few minutes and try again."
                )


# ─────────────────────────────────────────────────────────────
# CORE ENGINE — TWO-STEP ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyse_listing(
    image_paths: list[str],
    location: str,
    budget: float,
    currency: str = "RM",
    listing_type: str = DEFAULT_LISTING_TYPE,
    corrections: str = "",
    guest_report: str = "",
    competitor_avg_score: float | None = None,
    shopping_preference: str = "both",
    goal: str = DEFAULT_GOAL
) -> dict:
    """
    Two-step analysis pipeline:

    STEP 1 — Visual Inventory (images → structured description)
        All photos sent to the API. The model describes what it sees
        objectively — no scoring yet. This separates observation from judgement
        and reduces hallucination in the scoring step.

    STEP 2 — Stager's Logic Scoring (inventory text → scored report)
        The inventory JSON from Step 1 is sent as text only (no images).
        The model applies scoring weights, generates recommendations,
        and produces the final report. Text-only = faster + cheaper.
    """
    signal.alarm(PROCESS_TIMEOUT)
    try:
        # ── STEP 1: Visual Inventory ───────────────────────────
        print("  Step 1/2: Building Visual Inventory...")
        inv_content = [{"type": "text", "text": INVENTORY_PROMPT}]
        for path in image_paths:
            b64, mime = optimise_and_encode(path)
            inv_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{b64}",
                    "detail": "high"
                }
            })

        inv_raw  = call_api_with_backoff(
            [{"role": "user", "content": inv_content}],
            max_tokens=1500,
            label="Inventory"
        )
        inventory = json.loads(inv_raw)
        print(f"  Inventory complete — {len(inventory.get('rooms', []))} room(s) documented.")

        # ── STEP 2: Stager's Logic Scoring (text only) ─────────
        print("  Step 2/2: Applying Stager's Logic scoring...")
        scoring_prompt = build_scoring_prompt(
            inventory=inventory,
            location=location,
            budget=budget,
            currency=currency,
            listing_type=listing_type,
            corrections=corrections,
            guest_report=guest_report,
            competitor_avg_score=competitor_avg_score,
            shopping_preference=shopping_preference,
            goal=goal
        )

        score_raw = call_api_with_backoff(
            [{"role": "user", "content": scoring_prompt}],
            max_tokens=3000,
            label="Scoring"
        )
        report = json.loads(score_raw)

        # Attach the raw inventory to the report for transparency
        report["_visual_inventory"] = inventory
        return report

    finally:
        signal.alarm(0)


# ─────────────────────────────────────────────────────────────
# PRETTY PRINTER
# ─────────────────────────────────────────────────────────────

def print_report(report: dict, currency: str = "RM") -> None:
    score    = report["vitality_score"]
    grade    = report["grade"]
    lt       = LISTING_TYPES.get(report.get("listing_type", ""), {}).get("label", "")
    bar      = "█" * (score // 5) + "░" * (20 - score // 5)
    ck       = f"estimated_cost_{currency.lower()}"
    tk       = f"shopping_list_total_{currency.lower()}"

    print(f"\n{'━'*58}")
    print(f"  VISUAL VITALITY SCORE:  {score}/100   Grade: {grade}")
    if lt:
        print(f"  Listing Type: {lt}")
    print(f"  {bar}")
    print(f"{'━'*58}")
    print(f"\n📋 SUMMARY\n{report['summary']}\n")

    print("📊 DIMENSION BREAKDOWN")
    for key, label in [
        ("colour_coherence",   "Colour Coherence"),
        ("lighting_quality",   "Lighting Quality"),
        ("functional_anchors", "Functional Anchors"),
        ("clutter_space_flow", "Clutter & Space Flow"),
        ("staging_integrity",  "Staging Integrity"),
    ]:
        d = report["dimensions"][key]
        print(f"  {label:<22} {d['score']:>2}/20  —  {d['notes']}")

    # Market Position
    mp = report.get("market_position", {})
    if mp:
        print(f"\n📈 MARKET POSITION")
        avg  = mp.get("competitor_avg_score")
        pos  = mp.get("listing_vs_market", "unknown").upper()
        gap  = mp.get("gap_to_market")
        proj = mp.get("projected_score_after_fixes")
        print(f"  This listing:       {score}/100")
        if avg:
            gap_str = f"  (gap: {gap:+d} pts)" if gap else ""
            print(f"  Area average:       {avg}/100")
            print(f"  Position:           {pos}{gap_str}")
        if proj:
            print(f"  Projected (fixed):  {proj}/100")
        if note := mp.get("revenue_impact_note"):
            print(f"  💰 {note}")

    # Reality Gap
    rg = report.get("reality_gap", {})
    if rg.get("has_guest_report"):
        rg_score = rg.get("total_score", 0)
        severity = rg.get("severity", "unknown").upper()
        print(f"\n{'━'*58}")
        print(f"  REALITY GAP SCORE: {rg_score}/80   Severity: {severity}")
        print(f"{'━'*58}")
        print(f"\n{rg.get('summary', '')}\n")
        for key, label in [
            ("mould_hygiene",         "Mould & Hygiene"),
            ("plumbing_integrity",    "Plumbing Integrity"),
            ("pest_presence",         "Pest Presence"),
            ("electrical_fixtures",   "Electrical & Fixtures"),
            ("furniture_safety",      "Furniture Safety"),
            ("linen_bedding_quality", "Linen & Bedding"),
            ("props_fraud",           "Props Fraud"),
            ("host_responsiveness",   "Host Responsiveness"),
        ]:
            c = rg.get("categories", {}).get(key)
            if c:
                print(f"  {label:<22} {c['score']:>2}/10  —  {c['finding']}")
        for a in rg.get("safety_alerts", []):
            print(f"\n  ⚠️  SAFETY: {a}")

    if report.get("critical_flags"):
        print("\n🚨 CRITICAL FLAGS")
        for f in report["critical_flags"]:
            print(f"  • {f}")

    if report.get("photo_actions"):
        print("\n📸 PHOTO ACTIONS")
        icons = {
            "keep":                       "✅",
            "restyle_before_reshoot":     "🔄",
            "delete":                     "🗑️",
            "add_to_amenities_list_only": "📋"
        }
        for p in report["photo_actions"]:
            icon = icons.get(p["action"], "•")
            print(f"  {icon} [{p['action'].upper()}]  {p['photo_subject']}")
            print(f"       ↳ {p['reason']}")

    if report.get("quick_wins"):
        print("\n✅ QUICK WINS")
        for w in report["quick_wins"]:
            print(f"  • {w}")

    # Show It list — zero cost, high trust impact
    show_it = report.get("show_it_list", [])
    if show_it:
        print(f"\n📷 SHOW IT LIST  (items you have — just photograph them)")
        for s in show_it:
            print(f"  • {s['item']}")
            print(f"    ↳ Action: {s['action']}")
            print(f"    ↳ Impact: {s['impact']}")

    # Monetized shopping list — clean table
    items = report.get("shopping_list", [])
    if items:
        print(f"\n🛒 SHOPPING LIST  (items to buy)")
        print(f"  {'Item':<32} {'Cost':>8}  {'Type':<10}  Purchase Link")
        print(f"  {'─'*32} {'─'*8}  {'─'*10}  {'─'*28}")
        for item in items:
            cost     = item.get(ck, 0)
            sourcing = item.get("sourcing", "").upper()
            link     = item.get("purchase_link", "")
            alt_link = item.get("alternative_link", "")
            name     = item["item"][:31]
            print(f"  {name:<32} {currency}{cost:>7,.0f}  {sourcing:<10}  {link}")
            if alt_link:
                print(f"  {'':32}           Alt: {alt_link}")
            print(f"  {'':32}           Why: {item.get('why', '')}")
        total = report.get(tk, sum(i.get(ck, 0) for i in items))
        print(f"\n  {'TOTAL':<32} {currency}{total:>7,.0f}")

    # Visual Inventory summary
    inv = report.get("_visual_inventory", {})
    if inv.get("rooms"):
        print(f"\n🔍 VISUAL INVENTORY ({len(inv['rooms'])} room(s) documented)")
        for room in inv["rooms"]:
            print(f"  • {room['room_type'].upper()}")
            if room.get("missing_items"):
                for m in room["missing_items"]:
                    print(f"      ↳ Missing: {m}")
            if room.get("condition_notes"):
                for c in room["condition_notes"]:
                    print(f"      ↳ Note: {c}")

    print(f"\n{'━'*58}\n")


# ─────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Airbnb Visual Vitality Score Engine")
    parser.add_argument("--images",               nargs="+", required=True,
                        help=f"Image file paths (max {MAX_IMAGES})")
    parser.add_argument("--location",             default="Kuala Lumpur")
    parser.add_argument("--budget",               type=float, default=2000)
    parser.add_argument("--currency",             default="RM")
    parser.add_argument("--listing-type",         default=DEFAULT_LISTING_TYPE,
                        choices=list(LISTING_TYPES.keys()),
                        dest="listing_type",
                        help="urban_studio | resort | city_apartment | family_home")
    parser.add_argument("--corrections",          default="",
                        help="Host corrections overriding visual misreads")
    parser.add_argument("--guest-report",         default="", dest="guest_report",
                        help="Guest account of actual conditions on arrival")
    parser.add_argument("--competitor-avg-score", type=float, default=None,
                        dest="competitor_avg_score",
                        help="Average Vitality Score of comparable local listings")
    parser.add_argument("--all-images",           action="store_true", dest="all_images",
                        help="Send all images; skip smart hero selection")
    parser.add_argument("--shopping-preference",  default="both",
                        choices=list(SHOPPING_PREFERENCES.keys()),
                        dest="shopping_preference",
                        help="online | in_store | both | curated")
    parser.add_argument("--goal",                 default=DEFAULT_GOAL,
                        choices=list(HOST_GOALS.keys()),
                        help="rate | vacancy | rating | all")
    args = parser.parse_args()

    try:
        all_images = get_photos_from_source(args.images)
    except ValueError as e:
        print(f"\n❌ {e}\n")
        exit(1)

    # Smart hero selection (unless --all-images passed)
    if args.all_images or len(all_images) <= HERO_LIMIT:
        images  = all_images
        skipped = []
    else:
        images, skipped = select_hero_images(all_images)

    lt_label = LISTING_TYPES.get(args.listing_type, {}).get("label", args.listing_type)
    print(f"\nAnalysing {len(images)} image(s) | {args.location} | "
          f"{lt_label} | Budget: {args.currency} {args.budget:,.0f}")
    if skipped:
        print(f"  Smart selection: skipped {len(skipped)} lower-priority photo(s): "
              f"{', '.join(Path(p).name for p in skipped)}")
    if args.corrections:
        print("  ✎  Host corrections applied.")
    if args.guest_report:
        print("  👤 Guest reality report — Reality Gap will be calculated.")
    if args.competitor_avg_score:
        print(f"  📊 Competitor average: {args.competitor_avg_score}/100")

    try:
        report = analyse_listing(
            image_paths=images,
            location=args.location,
            budget=args.budget,
            currency=args.currency,
            listing_type=args.listing_type,
            corrections=args.corrections,
            guest_report=args.guest_report,
            competitor_avg_score=args.competitor_avg_score,
            shopping_preference=args.shopping_preference,
            goal=args.goal
        )
    except TimeoutError as e:
        print(f"\n⏱️  {e}\n")
        exit(1)
    except RuntimeError as e:
        print(f"\n❌ {e}\n")
        exit(1)

    print_report(report, currency=args.currency)

    out = Path("last_report.json")
    out.write_text(json.dumps(report, indent=2))
    print(f"Raw JSON saved → {out}")
