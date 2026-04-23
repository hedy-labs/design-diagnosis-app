"""
Vision Analyzer — Claude Vision for Photo Analysis

Analyzes listing photos for Design Diagnosis vitality scoring.
Evaluates: Lighting Quality, Functionality, Color Harmony, Clutter & Flow, Staging Integrity
"""

import logging
import base64
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import Claude
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  anthropic package not installed. Vision analysis will use mock mode.")
    CLAUDE_AVAILABLE = False


class VisionAnalyzer:
    """Claude Vision analysis for photos"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-3-5-sonnet-20241022"  # Use Sonnet for vision analysis
        
        if self.api_key and CLAUDE_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.mode = "LIVE"
                logger.info("✅ Claude Vision initialized (LIVE mode)")
            except Exception as e:
                logger.error(f"❌ Claude initialization failed: {e}")
                self.client = None
                self.mode = "MOCK"
        else:
            self.client = None
            self.mode = "MOCK"
            if not self.api_key:
                logger.warning("⚠️  ANTHROPIC_API_KEY not set. Using mock vision analysis.")
    
    def analyze_photo(self, image_path: str) -> Dict:
        """
        Analyze a single photo for design vitality.
        
        Returns: {
            'lighting_quality': 0-6,
            'functionality_flow': 0-6,
            'color_harmony': 0-6,
            'clutter_density': 0-6,
            'staging_integrity': 0-6,
            'guest_psychology': str,
            'summary': str
        }
        """
        try:
            if self.mode == "LIVE" and self.client and os.path.exists(image_path):
                return self._analyze_with_claude(image_path)
            else:
                return self._analyze_mock(image_path)
        
        except Exception as e:
            logger.error(f"❌ Vision analysis error: {e}")
            return self._get_default_scores()
    
    def _analyze_with_claude(self, image_path: str) -> Dict:
        """Analyze using real Claude Vision"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Determine media type
            ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(ext, 'image/jpeg')
            
            # Create the analysis prompt
            prompt = """Analyze this Airbnb/VRBO listing photo for design vitality and guest psychology.

Rate EACH dimension on a 0-6 scale and respond in JSON format:

{
  "lighting_quality": <0-6>,
  "functionality_flow": <0-6>,
  "color_harmony": <0-6>,
  "clutter_density": <0-6>,
  "staging_integrity": <0-6>,
  "guest_psychology": "<one sentence: how would a guest feel entering this space?>",
  "summary": "<one sentence: key design observation>"
}

DIMENSION DEFINITIONS:
- Lighting Quality: Brightness, ambiance, shadows, natural vs artificial. 0=Dark/Poor, 6=Bright/Perfect
- Functionality & Flow: Space usage, furniture arrangement, guest movement. 0=Cramped/Blocked, 6=Open/Intuitive
- Color Harmony: Palette coherence, warm/cool balance, visual appeal. 0=Chaotic, 6=Cohesive/Beautiful
- Clutter Density: Cleanliness, organization, visual simplicity. 0=Cluttered/Messy, 6=Clean/Minimalist
- Staging Integrity: Props, styling, professionalism, authenticity. 0=Fake/Over-staged, 6=Authentic/Professional

Guest Psychology: Emotional response—does this feel welcoming, clean, functional, trustworthy?

IMPORTANT: Be honest and specific. A beautiful living room with poor lighting gets 5/6 (not 6/6)."""
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Parse response
            response_text = response.content[0].text
            logger.info(f"✅ Claude vision analysis complete for {os.path.basename(image_path)}")
            logger.debug(f"Claude response: {response_text}")
            
            # Try to parse JSON from response
            import json
            try:
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Ensure all scores are 0-6
                    for key in ['lighting_quality', 'functionality_flow', 'color_harmony', 'clutter_density', 'staging_integrity']:
                        result[key] = max(0, min(6, result.get(key, 3)))
                    
                    return result
            except json.JSONDecodeError:
                logger.warning(f"⚠️  Could not parse Claude response as JSON")
            
            # Fallback to defaults if parsing fails
            return self._get_default_scores()
        
        except Exception as e:
            logger.error(f"❌ Claude vision error: {e}")
            return self._get_default_scores()
    
    def _analyze_mock(self, image_path: str) -> Dict:
        """Mock analysis (development/testing)"""
        logger.info(f"📋 [MOCK] Vision analysis for {os.path.basename(image_path)}")
        return {
            "lighting_quality": 4,
            "functionality_flow": 4,
            "color_harmony": 4,
            "clutter_density": 4,
            "staging_integrity": 3,
            "guest_psychology": "Comfortable and moderately well-designed, with room for improvement.",
            "summary": "Solid property with some design gaps in staging and lighting."
        }
    
    def _get_default_scores(self) -> Dict:
        """Return default scores when analysis fails"""
        return {
            "lighting_quality": 3,
            "functionality_flow": 3,
            "color_harmony": 3,
            "clutter_density": 3,
            "staging_integrity": 2,
            "guest_psychology": "Unable to analyze photo.",
            "summary": "Analysis failed - using conservative defaults."
        }
    
    def analyze_listing(self, image_paths: list) -> Dict:
        """
        Analyze multiple photos from a listing.
        
        Returns average scores and synthesis.
        """
        if not image_paths:
            return self._get_default_scores()
        
        analyses = []
        for image_path in image_paths:
            if os.path.exists(image_path):
                result = self.analyze_photo(image_path)
                analyses.append(result)
        
        if not analyses:
            return self._get_default_scores()
        
        # Average the scores
        avg = {
            'lighting_quality': sum(a.get('lighting_quality', 3) for a in analyses) / len(analyses),
            'functionality_flow': sum(a.get('functionality_flow', 3) for a in analyses) / len(analyses),
            'color_harmony': sum(a.get('color_harmony', 3) for a in analyses) / len(analyses),
            'clutter_density': sum(a.get('clutter_density', 3) for a in analyses) / len(analyses),
            'staging_integrity': sum(a.get('staging_integrity', 3) for a in analyses) / len(analyses),
        }
        
        # Round to nearest 0.5
        for key in avg:
            avg[key] = round(avg[key] * 2) / 2
        
        logger.info(f"✅ Analyzed {len(analyses)} photos. Average scores: {avg}")
        
        return avg
