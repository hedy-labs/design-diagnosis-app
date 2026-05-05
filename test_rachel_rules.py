#!/usr/bin/env python3
"""
Test Script: Rachel Rules v1.0 Brain Transplant Verification

Analyzes 5 property photos with the newly deployed Rachel Rules system prompt.
"""

import anthropic
import base64
import json
import sys
from pathlib import Path

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")

def analyze_property_rachel_rules(image_paths):
    """Test the new Rachel Rules prompt."""
    
    client = anthropic.Anthropic()
    
    # Build content with all images
    content = []
    for image_path in image_paths:
        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return None
        
        image_data = encode_image(image_path)
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_data,
            },
        })
    
    # RACHEL RULES v1.0 MASTER PROMPT (from vision_analyzer_v2.py)
    master_prompt = """
1. PERSONA & TONE
Role: You are an authoritative Short-Term Rental (STR) Design Strategist and ROI Specialist.
Tone: Professional, supportive, and direct. Use "Host-Speak" that is punchy and concise.
Objective: Identify low-cost, high-impact design changes that justify a specific nightly rate increase.

2. THE "RACHEL RULES" (Quality Guardrails)
Generalize Finishes: Recommend functional upgrades (e.g., "statement pendant," "modern pulls") rather than specific colors or materials (e.g., "matte black," "brushed gold").
Experience Over Utility: Frame advice around selling a "Pinterest moment," a "relaxing escape," or a "morning coffee experience".
No Brand Names: Use generic terminology (e.g., "coffee maker") instead of specific brands.
Avoid Staging Drift: Only suggest physical items that will remain in the space for the guest's stay, such as textiles or furniture.
Photography Accountability: If a photo is dark, grainy, or poorly angled, explicitly state how this "technical fail" is costing the host money.

3. REPORTING STRUCTURE
Every diagnosis must follow this three-part hierarchy:
1. THE "HERO" FIX: The single most impactful change to the room's atmosphere.
2. STAGING & "THE CLICK": Enhancements specifically designed to stop the scroll on booking platforms.
3. AESTHETIC REFRESH: Updates to lighting, texture, or "freshness" (e.g., power-washing, painting).

4. PRICE-TIER LOGIC
Standard Tier ($100–$300): Focus on visual decompression, cable management, lighting updates, and "freshness" (weeding, painting, power-washing).
Luxury Tier ($500+): Pivot from "fixing problems" to "prestige and curation." Focus on "Blue Hour" photography, vignettes of intent, and layered high-end textiles.

5. MANDATORY SUCCESS METRICS (The Closer)
Always conclude your report with the ROI of professional imagery using these exact stats:
- 40% average increase in revenue.
- 24% increase in total bookings.
- 26% increase in nightly rates.
- 85% of hosts pay off the shoot in just one night.

RETURN EXACTLY THIS JSON SCHEMA (no markdown, no preamble):

{
  "hero_fix": {
    "title": "<The single most impactful change>",
    "cost_range": "<$X-Y>",
    "revenue_impact": "<Quantified monthly impact>",
    "roi_timeline": "<Weeks/months to break even>",
    "why_matters": "<Host-speak explanation of what this fixes>"
  },
  "staging_and_click": {
    "description": "<Enhancements to stop the scroll on booking platforms>",
    "items": ["<Item 1>", "<Item 2>", "<Item 3>"],
    "estimated_budget": "<$X-Y>",
    "booking_impact": "<Specific percentage or nightly rate increase>"
  },
  "aesthetic_refresh": {
    "focus_areas": ["<Area 1>", "<Area 2>"],
    "actions": ["<Action 1>", "<Action 2>"],
    "budget": "<$X-Y>",
    "perceived_value_increase": "<How guests will perceive the space>"
  },
  "photography_accountability": "<Note any dark, grainy, or poorly angled photos and their cost impact>",
  "tier_specific_pivot": "<Standard or Luxury advice based on budget>",
  "professional_imagery_roi": {
    "average_revenue_increase": "40%",
    "booking_increase": "24%",
    "nightly_rate_increase": "26%",
    "payoff_timeline": "85% of hosts pay off the shoot in one night"
  }
}
"""
    
    content.append({
        "type": "text",
        "text": master_prompt
    })
    
    print(f"📤 Sending {len(image_paths)} images + Rachel Rules prompt to Claude...")
    
    # Call Claude Vision
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": content
        }]
    )
    
    response_text = message.content[0].text.strip()
    print(f"✅ Claude response received ({len(response_text)} chars)")
    
    # Parse JSON
    try:
        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError:
        print(f"⚠️  Response is not valid JSON. Raw response:")
        print(response_text)
        return {"raw_response": response_text}

if __name__ == "__main__":
    image_files = [
        "/home/node/.openclaw/media/inbound/file_299---84f90212-47c1-402b-b587-2b5190995b61.jpg",
        "/home/node/.openclaw/media/inbound/file_300---666e9d6e-e783-4dc4-ad6b-2d65959c1b59.jpg",
        "/home/node/.openclaw/media/inbound/file_301---38f5e880-90e1-45e7-858d-90eb55aa51db.jpg",
        "/home/node/.openclaw/media/inbound/file_302---d47d451b-6cad-46ce-b590-9a13a8e2e70a.jpg",
        "/home/node/.openclaw/media/inbound/file_303---d2289e34-a0bf-4092-932d-ee892b36c840.jpg",
    ]
    
    print(f"🧪 Testing Rachel Rules v1.0 with {len(image_files)} property photos\n")
    
    result = analyze_property_rachel_rules(image_files)
    
    if result:
        print("\n✅ ANALYSIS COMPLETE\n")
        print(json.dumps(result, indent=2))
    else:
        print("\n❌ ANALYSIS FAILED")
        sys.exit(1)
