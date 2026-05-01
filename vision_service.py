"""
Vision Service — Google Gemini 1.5 Pro Integration

Analyzes property photos against 5 Pillars using expert design prompts.
Returns structured JSON with "Vibe → Expert Why → Fix" narrative format.
"""

import json
import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import base64

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  google-generativeai not installed. Vision analysis unavailable.")
    GEMINI_AVAILABLE = False


@dataclass
class VibeFinding:
    """Single design finding with 3-part narrative"""
    room: str
    issue_type: str  # e.g., "insufficient_light_sources", "cool_white_bulb"
    the_vibe: str  # How guest feels (sensory language)
    expert_why: str  # Plain English design principle
    the_fix: str  # Actionable improvement
    score: float  # 0–10 for this specific issue
    cost_low: Optional[int] = None
    cost_high: Optional[int] = None


@dataclass
class PillarAnalysis:
    """Complete Pillar 2 analysis result"""
    pillar_name: str = "Lighting & Optical Health"
    pillar_score: float = 0.0  # 0–10
    findings: List[VibeFinding] = None  # List of issues with Vibe → Why → Fix
    room_summaries: Dict = None  # Per-room breakdown
    pillar_narrative: str = ""  # Overall assessment
    priority_fixes: List[Dict] = None  # Cost-sorted fixes


class VisionService:
    """
    Google Gemini 1.5 Pro Vision Analysis
    
    Analyzes property photos against 5 Pillars.
    Returns structured findings in "Vibe → Expert Why → Fix" format.
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-vision-latest')
            self.ready = True
            logger.info("✅ Gemini 1.5 Pro Vision ready")
        else:
            self.ready = False
            if not self.api_key:
                logger.warning("⚠️  GEMINI_API_KEY not set")
            if not GEMINI_AVAILABLE:
                logger.warning("⚠️  google-generativeai not installed")
    
    def analyze_pillar_2_lighting(self, images: List[str]) -> PillarAnalysis:
        """
        Analyze property photos for Pillar 2: Lighting & Optical Health
        
        Args:
            images: List of image file paths or base64 strings
        
        Returns:
            PillarAnalysis with findings in "Vibe → Expert Why → Fix" format
        """
        if not self.ready:
            logger.error("❌ Vision service not ready (Gemini API unavailable)")
            return self._default_pillar_2_response()
        
        logger.info(f"🎬 Analyzing {len(images)} photos for Pillar 2: Lighting & Optical Health")
        
        # Build image content for Gemini
        content = []
        
        for idx, image_path in enumerate(images[:10]):  # Max 10 images per call
            logger.info(f"   Loading image {idx+1}: {image_path[:50]}...")
            
            try:
                if image_path.startswith('data:'):
                    # Already base64
                    content.append({
                        'type': 'image',
                        'source': {'type': 'base64', 'data': image_path.split(',')[1]}
                    })
                elif os.path.exists(image_path):
                    # Local file
                    with open(image_path, 'rb') as f:
                        image_data = base64.standard_b64encode(f.read()).decode('utf-8')
                    
                    # Detect MIME type
                    ext = os.path.splitext(image_path)[1].lower()
                    mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
                    mime_type = mime_map.get(ext, 'image/jpeg')
                    
                    content.append({
                        'type': 'image',
                        'source': {'type': 'base64', 'data': image_data, 'media_type': mime_type}
                    })
                else:
                    logger.warning(f"   ⚠️  Image not found: {image_path}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to load image: {e}")
        
        # Add system prompt
        content.append({
            'type': 'text',
            'text': self._get_pillar_2_prompt()
        })
        
        logger.info("🤖 Sending to Gemini 1.5 Pro...")
        
        try:
            response = self.model.generate_content(content)
            
            if response and response.text:
                logger.info(f"✅ Gemini response received ({len(response.text)} chars)")
                
                # Parse JSON response
                try:
                    json_start = response.text.find('{')
                    json_end = response.text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = response.text[json_start:json_end]
                        result_dict = json.loads(json_str)
                        
                        # Convert to PillarAnalysis object
                        analysis = self._parse_pillar_analysis(result_dict)
                        logger.info(f"✅ Analysis parsed: pillar_score={analysis.pillar_score}/10")
                        
                        return analysis
                    else:
                        logger.error("❌ Could not find JSON in Gemini response")
                        return self._default_pillar_2_response()
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parse error: {e}")
                    logger.error(f"Response text: {response.text[:500]}")
                    return self._default_pillar_2_response()
            else:
                logger.error("❌ Empty Gemini response")
                return self._default_pillar_2_response()
        
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_pillar_2_response()
    
    def _get_pillar_2_prompt(self) -> str:
        """Return the Pillar 2 (Lighting) system prompt with Human Voice tone"""
        return """You are a high-end interior design consultant, not a building code auditor.

Your job: Analyze these property photos for lighting design, focusing on how guests will FEEL and experience the space.

This is Pillar 2: "Lighting & Optical Health" — part of a comprehensive design assessment for homeowners.

TONE REQUIREMENT:
- Never output "Rule #X Violation" or building-code language
- For every issue found, explain it in 3 parts:
  1. The Vibe: How the guest emotionally experiences the problem (sensory, honest)
  2. The Expert Why: Design principle explanation in plain English
  3. The Fix: Specific, actionable improvement with cost range
- Speak like Rachel: warm, expert, human-centered (not robotic)

CRITICAL RULES TO CHECK:

Rule #51: "Warm Over Cool" (Kelvin Color Temperature)
- SUCCESS: All visible bulbs are 2700K–3000K warm white (yellow-toned, like candlelight)
- FAILURE: Bulbs appear cool white 5000K+ (like hospital/office fluorescents)
- FAILURE: Mixed temperatures in same room (some warm, some cool = disorienting)

Rule #53: "Three Points of Light" (Light Source Variety)
- SUCCESS: Room has 3+ distinct light sources: (1) Overhead, (2) Task lamp, (3) Ambient/mood
- PARTIAL: Room has 2 types (e.g., overhead + task, but no ambient)
- FAILURE: Room has only 1 light source (ceiling fixture only = "Visual Interrogation")

Rule #55: "Reflective Magic" (Mirror Light Bouncing)
- SUCCESS: Mirrors positioned opposite or near windows to bounce natural light into dark corners
- FAILURE: Mirror present but facing wall or in bright area (wasting potential)

Rule #52: "The Eye-Level Rule" (Lampshade Position)
- SUCCESS: Lampshades sit at guest eye level when seated (prevents glare from naked bulb)
- FAILURE: Lamp too high (guest sees bright bulb = glare) or too low (shadow on book/face)

Bathroom-specific:
- Mirror must have side lighting (vanity lights) OR top lighting that illuminates face
- Ceiling-only light creates eye shadow = guest looks tired in mirror

Bedroom-specific:
- Bedroom must have thick, opaque blackout curtains/shades with NO visible light leaks at edges
- Light leaking around curtains = guests can't sleep past dawn = poor reviews

ANALYSIS WORKFLOW:
1. Examine each room photo carefully
2. For each issue found, create a finding with: room, issue_type, the_vibe, expert_why, the_fix, score
3. Score each issue 0–10 (10=perfect, 0=critical failure)
4. Provide room-by-room summary
5. Calculate overall pillar_score as average of all issues
6. Return ONLY valid JSON (no markdown, no extra text)

REQUIRED JSON RESPONSE FORMAT (EXACTLY):
{
  "pillar_name": "Lighting & Optical Health",
  "pillar_score": <average of all issue scores 0-10>,
  "findings": [
    {
      "room": "<room name>",
      "issue_type": "<issue_type>",
      "the_vibe": "<how guest feels - sensory language>",
      "expert_why": "<plain English design principle>",
      "the_fix": "<specific actionable improvement>",
      "score": <0-10>,
      "cost_low": <optional int>,
      "cost_high": <optional int>
    }
  ],
  "room_summaries": {
    "<room_name>": {
      "overall_feel": "<guest experience summary>",
      "wins": ["<positive finding>"],
      "gaps": ["<issue to fix>"]
    }
  },
  "pillar_narrative": "<overall assessment paragraph>",
  "priority_fixes": [
    {
      "priority": 1,
      "fix_name": "<fix name>",
      "cost_low": <int>,
      "cost_high": <int>,
      "impact": "<High/Medium/Low>"
    }
  ]
}

IMPORTANT: Return ONLY valid JSON. No introductory text, no markdown. Start with '{' and end with '}'."""
    
    def _parse_pillar_analysis(self, data: Dict) -> PillarAnalysis:
        """Convert raw JSON to PillarAnalysis dataclass"""
        findings = []
        
        if 'findings' in data:
            for f in data['findings']:
                findings.append(VibeFinding(
                    room=f.get('room', ''),
                    issue_type=f.get('issue_type', ''),
                    the_vibe=f.get('the_vibe', ''),
                    expert_why=f.get('expert_why', ''),
                    the_fix=f.get('the_fix', ''),
                    score=float(f.get('score', 5.0)),
                    cost_low=f.get('cost_low'),
                    cost_high=f.get('cost_high')
                ))
        
        return PillarAnalysis(
            pillar_name=data.get('pillar_name', 'Lighting & Optical Health'),
            pillar_score=float(data.get('pillar_score', 5.0)),
            findings=findings,
            room_summaries=data.get('room_summaries', {}),
            pillar_narrative=data.get('pillar_narrative', ''),
            priority_fixes=data.get('priority_fixes', [])
        )
    
    def _default_pillar_2_response(self) -> PillarAnalysis:
        """Return default response when Gemini API unavailable"""
        logger.info("📋 [MOCK] Returning default Pillar 2 response")
        
        return PillarAnalysis(
            pillar_name="Lighting & Optical Health",
            pillar_score=5.0,
            findings=[
                VibeFinding(
                    room="test_room",
                    issue_type="mock_test",
                    the_vibe="Mock test mode - no actual analysis",
                    expert_why="Gemini API not configured",
                    the_fix="Configure GEMINI_API_KEY environment variable",
                    score=5.0
                )
            ],
            room_summaries={},
            pillar_narrative="Mock response for testing",
            priority_fixes=[]
        )


# Test execution
if __name__ == "__main__":
    import sys
    
    # Initialize service
    service = VisionService()
    
    if not service.ready:
        print("⚠️  Gemini API not available. Cannot run Vision test.")
        print("   Set GEMINI_API_KEY environment variable to enable.")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("VISION SERVICE TEST: Pillar 2 (Lighting & Optical Health)")
    print("="*70)
    print("\nTo run test with actual images:")
    print("  python3 vision_service.py [image_path_1] [image_path_2] ...")
    print("\nExample:")
    print("  python3 vision_service.py photo1.jpg photo2.jpg photo3.jpg")
    print("\nCurrent status: Gemini API ready")
    print("="*70 + "\n")
