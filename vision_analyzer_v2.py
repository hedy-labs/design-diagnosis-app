"""
Vision Analyzer V2 — Batch Claude Vision Analysis for Property Photos

Analyzes multiple property photos in parallel, deduplicates by perceptual hash,
and aggregates design scores for vitality calculation.

UPDATED: ROI Intelligence Injection (v3.0)
- All outputs validated for revenue-first justifications
- No designer speak allowed
- All recommendations include payback periods
"""

import logging
import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple
import imagehash
from PIL import Image
from io import BytesIO
import httpx

logger = logging.getLogger(__name__)

# Import ROI validator
try:
    from roi_validator import validate_vision_output, validate_lite_response
except ImportError:
    logger.warning("⚠️  roi_validator not found, ROI validation disabled")
    validate_vision_output = None
    validate_lite_response = None


class VisionAnalyzerV2:
    """Batch vision analysis for property photos"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        # DYNAMIC MODEL VERSIONING: Load from .env file for flexibility
        # Default to latest if not configured
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
        logger.info(f"🤖 Vision Analyzer initialized with model: {self.model}")
    
    async def analyze_images_batch(self, image_urls: List[str], max_images: int = 20) -> Dict:
        """
        Analyze entire property holistically using all uploaded images.
        
        PHASE 3: Single Claude call with all images, returns holistic design scorecard.
        
        📊 PREMIUM TIER: Maximum 20 photos for comprehensive analysis
        
        Args:
            image_urls: List of direct image URLs (from photo scraper) OR base64 data URIs
            max_images: Max images to analyze (default 20 for Premium Tier)
        
        Returns:
            {
                'design_scorecard': {
                    'lighting_quality': 0-6,
                    'color_harmony': 0-6,
                    'clutter_density': 0-6,
                    'staging_integrity': 0-6,
                    'functionality': 0-6,
                    'total_design_score': 0-30
                },
                'honest_marketing_status': 'High Trust|Medium Trust|Low Trust',
                'top_3_fixes': [
                    {'priority': 1-3, 'title': str, 'experience_logic_rationale': str}
                ],
                'room_by_room_diagnosis': [
                    {'room': str, 'diagnosis': str, 'actionable_subtractions': [], 'actionable_additions': []}
                ]
            }
        """
        
        if not image_urls:
            logger.warning("⚠️  No images provided, using default scores")
            return self._default_scores()
        
        try:
            # Smart sample images
            logger.info(f"📸 Deduplicating {len(image_urls)} images...")
            print(f"[VISION] 📸 Deduplicating {len(image_urls)} images...")
            sampled = await self._smart_sample(image_urls, max_count=max_images)
            logger.info(f"✅ Sampled {len(sampled)} unique images for holistic analysis")
            print(f"[VISION] ✅ Using {len(sampled)} unique images for analysis")
            
            # PHASE 3: Single holistic Claude call with ALL images
            logger.info(f"🤖 Starting HOLISTIC analysis of entire property...")
            print(f"[VISION] 🤖 PHASE 3: Holistic property analysis (single Claude call)")
            
            result = await self._analyze_property_holistically(sampled)
            
            logger.info(f"✅ Holistic analysis complete")
            print(f"[VISION] ✅ Holistic analysis complete")
            return result
        
        except Exception as e:
            logger.error(f"❌ Holistic analysis error: {e}")
            print(f"[VISION] ❌ Analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info("📧 Falling back to default scores")
            return self._default_scores()
    
    async def analyze_images_batch_lite(self, image_urls: List[str], max_images: int = 5) -> Dict:
        """
        🆓 LITE ANALYSIS: Minimal-token zero-shot analysis for Free Tier
        
        Token budget: ~500 tokens (vs. 2000+ for premium)
        Output: Baseline 0-30 score + 3 major gaps
        Quality: Good enough for "should I upgrade?" preview
        
        Args:
            image_urls: List of image URLs
            max_images: Max images (default 5 for lite)
        
        Returns:
            {
                'lite_score': 0-30,  # Scaled differently than premium (0-100)
                'gaps': ['gap 1', 'gap 2', 'gap 3'],
                'assessment': 'brief summary'
            }
        """
        
        if not image_urls:
            logger.warning("⚠️  No images for lite analysis")
            return {
                'lite_score': 0,
                'gaps': ['Unable to analyze', 'Please upload photos', 'Try Premium for details'],
                'assessment': 'Analysis unavailable'
            }
        
        try:
            # Sample just 5 images for lite (save tokens)
            sampled = image_urls[:max_images]
            logger.info(f"🆓 LITE: Sampling {len(sampled)} images (token-efficient)")
            
            result = await self._analyze_lite_minimal(sampled)
            return result
        
        except Exception as e:
            logger.error(f"❌ Lite analysis failed: {e}")
            return {
                'lite_score': 0,
                'gaps': ['Analysis error', 'Try again', 'Upgrade to Premium'],
                'assessment': 'Analysis failed'
            }
    
    async def _analyze_lite_minimal(self, image_urls: List[str]) -> Dict:
        """
        PHASE 3: Single Claude Vision call analyzing ALL images together.
        Returns holistic design scorecard with room diagnosis and fix recommendations.
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            logger.info(f"📤 Sending {len(image_urls)} images to Claude for holistic analysis...")
            print(f"[VISION] 📤 Building multi-image request for Claude...")
            
            # Build content array with all images
            content = []
            
            # Add all images to content
            for idx, image_url in enumerate(image_urls):
                logger.info(f"   Adding image {idx + 1}/{len(image_urls)} to payload...")
                
                if image_url.startswith("data:"):
                    # Base64 data URI
                    image_source = self._parse_data_uri(image_url)
                else:
                    # HTTP URL
                    image_source = {"type": "url", "url": image_url}
                
                content.append({
                    "type": "image",
                    "source": image_source
                })
            
            # Add master prompt text
            master_prompt = """You are an elite interior designer and hospitality strategist. Analyze this ENTIRE property holistically across all provided photos.

RETURN EXACTLY THIS JSON SCHEMA (no markdown, no preamble):

{
  "design_scorecard": {
    "lighting_quality": <0-6>,
    "color_harmony": <0-6>,
    "clutter_density": <0-6>,
    "staging_integrity": <0-6>,
    "functionality": <0-6>,
    "total_design_score": <sum of above, 0-30>
  },
  "honest_marketing_status": "<High Trust | Medium Trust | Low Trust>",
  "top_3_fixes": [
    {
      "priority": <1-3>,
      "title": "<Blunt, actionable title>",
      "experience_logic_rationale": "<Why this matters for guest experience>"
    }
  ],
  "room_by_room_diagnosis": [
    {
      "room": "<Name of room detected>",
      "diagnosis": "<Critical evaluation of layout and staging>",
      "actionable_subtractions": ["<Item to remove>"],
      "actionable_additions": ["<Item to add>"]
    }
  ]
}

SCORING GUIDE:
- Lighting: Overhead only=1, Task+accent layering=6
- Color: Clashing tones=0, Intentional palette=6
- Clutter: Overwhelming visual noise=0, Serene breathing room=6
- Staging: Bare/mismatched=0, Professional designer-curated=6
- Functionality: No guest amenities=0, Intuitive luxury layout=6

EXPERIENCE LOGIC: How do these spaces MAKE GUESTS FEEL? Honest marketing = photos match reality."""
            
            content.append({
                "type": "text",
                "text": master_prompt
            })
            
            print(f"[VISION] 📤 Sending {len(image_urls)} images + master prompt to Claude...")
            
            # Single API call with all images
            message = client.messages.create(
                model=self.model,
                max_tokens=2000,  # Increased for holistic response
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )
            
            print(f"[VISION] ✅ Claude response received")
            
            # Parse response
            response_text = message.content[0].text.strip()
            
            # Handle markdown code blocks
            if '```' in response_text:
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            
            logger.info(f"✅ Holistic analysis parsed successfully")
            logger.info(f"   Design Score: {result['design_scorecard']['total_design_score']}/30")
            logger.info(f"   Trust Status: {result['honest_marketing_status']}")
            logger.info(f"   Top Fix: {result['top_3_fixes'][0]['title']}")
            
            print(f"[VISION] ✅ Result: {result['design_scorecard']['total_design_score']}/30")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Holistic analysis failed: {e}")
            print(f"[VISION] ❌ Holistic analysis error: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    async def _smart_sample(self, image_urls: List[str], max_count: int = 10) -> List[str]:
        """
        Deduplicate images using perceptual hashing.
        Returns highest-quality unique images, prioritizing different rooms.
        """
        
        if len(image_urls) <= max_count:
            return image_urls
        
        logger.info(f"🔄 Deduplicating {len(image_urls)} images...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Download and hash images
                hashes = {}
                
                for i, url in enumerate(image_urls[:max_count * 2]):  # Sample from top 2x
                    try:
                        logger.info(f"   Hashing image {i+1}...")
                        resp = await client.get(url, follow_redirects=True)
                        img = Image.open(BytesIO(resp.content))
                        
                        # Resize for consistent hashing
                        img.thumbnail((256, 256))
                        
                        # Perceptual hash
                        h = str(imagehash.average_hash(img))
                        
                        if h not in hashes:
                            hashes[h] = url
                    
                    except Exception as e:
                        logger.warning(f"   ⚠️  Failed to hash {url[:50]}...: {e}")
                        continue
                
                # Return unique URLs
                unique = list(hashes.values())[:max_count]
                logger.info(f"✅ Deduplication complete: {len(unique)} unique images")
                return unique
        
        except Exception as e:
            logger.warning(f"⚠️  Deduplication failed: {e}. Using original URLs.")
            return image_urls[:max_count]
    
    async def _analyze_lite_minimal(self, image_urls: List[str]) -> Dict:
        """
        🆓 LITE ANALYSIS IMPLEMENTATION: Zero-shot, minimal tokens
        
        Calls Claude with VISION_PROMPT_LITE (no examples, no few-shot)
        Returns JSON-only response with baseline score (0-30) and 3 gaps
        """
        
        # Load lite prompt template
        lite_prompt_path = os.path.join(os.path.dirname(__file__), "VISION_PROMPT_LITE.md")
        
        try:
            with open(lite_prompt_path, 'r') as f:
                prompt_content = f.read()
        except FileNotFoundError:
            logger.warning(f"⚠️  VISION_PROMPT_LITE.md not found, using fallback prompt")
            prompt_content = """
You are a property design reviewer. Analyze the photos and return ONLY JSON:
{
  "design_score": <0-30>,
  "gap_1": "<gap>",
  "gap_2": "<gap>",
  "gap_3": "<gap>",
  "brief_assessment": "<summary>"
}
"""
        
        # Prepare image data for Claude
        content = [{"type": "text", "text": prompt_content}]
        
        # Add images (support both cloud URLs and local data URIs)
        for image_url in image_urls:
            try:
                # Cloud URLs (S3/R2): Pass directly to Claude
                if image_url.startswith('http://') or image_url.startswith('https://'):
                    logger.info(f"📸 Using cloud URL: {image_url[:60]}...")
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": image_url
                        }
                    })
                
                # Local data URIs: Convert to base64
                elif image_url.startswith('data:'):
                    image_data = await self._fetch_image_data(image_url)
                    if image_data:
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        })
                
                else:
                    logger.warning(f"⚠️  Unknown image URL format: {image_url[:60]}...")
            
            except Exception as e:
                logger.warning(f"⚠️  Failed to process image for lite: {e}")
                continue
        
        try:
            # Call Claude API (synchronous call wrapped in async)
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            logger.info("🤖 Calling Claude for lite analysis...")
            response = client.messages.create(
                model=self.model,
                max_tokens=500,  # Lite = short response
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text.strip()
            
            # Parse JSON (should be pure JSON)
            import json
            result = json.loads(response_text)
            
            # ============================================================
            # ROI VALIDATION (NEW): Ensure revenue-first justifications
            # ============================================================
            if validate_vision_output:
                is_valid, validated_result = validate_vision_output(result, analysis_type='lite')
                if not is_valid:
                    logger.warning("⚠️  Lite response failed ROI validation, using best-effort result")
                result = validated_result
            
            logger.info(f"✅ Lite analysis complete: score={result.get('design_score', 0)}/30")
            
            # Return structured response with ROI fields
            return {
                'lite_score': result.get('design_score', 0),
                'gaps': [
                    result.get('gap_1', 'N/A'),
                    result.get('gap_2', 'N/A'),
                    result.get('gap_3', 'N/A')
                ],
                'roi_justifications': [
                    result.get('roi_why_1', 'ROI analysis pending'),
                    result.get('roi_why_2', 'ROI analysis pending'),
                    result.get('roi_why_3', 'ROI analysis pending')
                ],
                'assessment': result.get('brief_assessment', 'Analysis complete'),
                'raw_response': result  # Include full response for transparency
            }
        
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to parse lite response as JSON: {response_text[:100]}")
            return {
                'lite_score': 15,  # Default middle score
                'gaps': ['Unable to parse analysis', 'Please try Premium', 'For full details'],
                'assessment': 'Analysis incomplete'
            }
        
        except Exception as e:
            logger.error(f"❌ Lite analysis error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'lite_score': 0,
                'gaps': ['Analysis failed', 'Try again', 'Contact support'],
                'assessment': 'Error during analysis'
            }
    
    async def _analyze_single_image(self, image_url: str) -> Dict:
        """
        Analyze one image using Claude Vision API (URL or base64).
        
        Returns: {
            'success': bool,
            'lighting': 0-6,
            'colors': 0-6,
            'clutter': 0-6,
            'staging': 0-6,
            'functionality': 0-6,
            'room_type': str,
            'notes': str
        }
        """
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            logger.info(f"   🔍 Analyzing: {image_url[:60]}...")
            print(f"[VISION] 🔍 Starting single image analysis")
            
            # Determine if URL or base64-encoded data URI
            if image_url.startswith("data:"):
                # Base64-encoded image data URI
                logger.info(f"   📷 Processing base64-encoded image...")
                print(f"[VISION] 📷 Parsing data URI (base64 image)")
                image_source = self._parse_data_uri(image_url)
            else:
                # HTTP URL
                print(f"[VISION] 🌐 Using HTTP URL image source")
                image_source = {
                    "type": "url",
                    "url": image_url
                }
            
            print(f"[VISION] 📤 Sending to Claude API: {self.model}")
            message = client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": image_source
                            },
                            {
                                "type": "text",
                                "text": """You are an elite interior designer and hospitality strategist analyzing a short-term rental property for guest experience quality.

Adopt the STRATEGIC DESIGNER PERSONA: Look beyond inventory. Analyze EXPERIENCE LOGIC—the invisible guest journey through each space. How does the design MAKE GUESTS FEEL?

ANALYZE THESE EXPERIENCE DIMENSIONS:

1. **Lighting Quality** (0-6: dark→perfect ambiance)
   - Not just brightness, but warmth. Overhead only = cold (1). Layered with task + accent = inviting (6).
   - Morning light quality. Evening mood. Bathroom safety vs. master bedroom romance.

2. **Color Harmony** (0-6: clashing→sophisticated)
   - Professional palette coherence. Intentional or accidental?
   - Does color SUPPORT the experience or DISTRACT from it?
   - Warm/cool consistency across rooms (switching color temperature = disorienting).

3. **Clutter Density** (0-6: overwhelmed→serene)
   - Not storage quantity, but VISUAL REST. Can guests relax or do they feel in a museum?
   - Personal items vs. staging props. Is this a HOME or a HOTEL?

4. **Staging Integrity** (0-6: neglected→designer-curated)
   - Professional decor choices (paired nightstands, console behind sofa, entry hooks) = guest confidence.
   - Bare/mismatched (single nightstand, no seating plan) = "did they try?"
   - Evidence of CARE vs. INDIFFERENCE.

5. **Functionality** (0-6: survival→luxury)
   - Visible guest needs: workspace (laptop), seating logic, storage for luggage, bathroom workflow.
   - Not just presence but ACCESSIBILITY. Can a guest find these things intuitively?

6. **Honest Marketing** (hidden signal)
   - If photos show wine/chocolate staging NOT provided = TRUST BREAK.
   - If furniture is oversized for room = CLAUSTROPHOBIA.
   - Inconsistent bedroom shots = guest arrives to surprise (bad).

ROOM TYPE DETECTION:
- kitchen, bedroom, bathroom, living, entry, storage, other

STRATEGIC NOTES: 
- What is the emotional FIRST IMPRESSION of this space?
- What design choices show HOST INVESTMENT vs. LOW EFFORT?
- If you stayed here, would you trust the listing photos?

Return ONLY valid JSON (no markdown, no preamble):
{
    "lighting": 0-6,
    "colors": 0-6,
    "clutter": 0-6,
    "staging": 0-6,
    "functionality": 0-6,
    "room_type": "kitchen|bedroom|bathroom|living|entry|storage|other",
    "trust_signal": "high|medium|low",
    "strategic_notes": "1-2 sentences on guest experience and host investment"
}"""
                            }
                        ]
                    }
                ]
            )
            
            print(f"[VISION] ✅ API response received")
            
            # Parse response
            response_text = message.content[0].text.strip()
            
            # Handle markdown code blocks
            if '```' in response_text:
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            result['success'] = True
            
            logger.info(f"   ✅ Analyzed: {result['room_type']} (staging: {result['staging']}/6)")
            print(f"[VISION] ✅ Analysis complete: {result['room_type']} (staging: {result['staging']}/6)")
            return result
        
        except Exception as e:
            print(f"[VISION] ❌ CRITICAL ERROR IN _analyze_single_image:")
            print(f"[VISION]    Exception type: {type(e).__name__}")
            print(f"[VISION]    Error message: {str(e)}")
            import traceback
            print(f"[VISION]    Traceback:")
            for line in traceback.format_exc().split('\n'):
                if line:
                    print(f"[VISION]      {line}")
            logger.error(f"   ❌ Analysis failed: {e}")
            logger.error(f"      Exception type: {type(e).__name__}")
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e), 'error_type': type(e).__name__}
    
    def _parse_data_uri(self, data_uri: str) -> Dict:
        """
        Parse data URI and convert to Claude Vision API base64 format.
        
        Input: data:image/jpeg;base64,/9j/4AAQSkZJRg...
        Output: {"type": "base64", "media_type": "image/jpeg", "data": "/9j/4AAQSkZJRg..."}
        """
        try:
            # Extract parts: data:image/jpeg;base64,{base64_data}
            if not data_uri.startswith("data:"):
                raise ValueError("Invalid data URI format")
            
            # Remove "data:" prefix
            rest = data_uri[5:]
            
            # Split on comma to get mime type and data
            parts = rest.split(',', 1)
            if len(parts) != 2:
                raise ValueError("Malformed data URI")
            
            mime_part, base64_data = parts
            
            # Extract MIME type (e.g., "image/jpeg;base64" -> "image/jpeg")
            if ';' in mime_part:
                media_type = mime_part.split(';')[0]
            else:
                media_type = mime_part or "image/jpeg"
            
            logger.info(f"   📷 Data URI parsed: {media_type}, {len(base64_data)} bytes")
            
            return {
                "type": "base64",
                "media_type": media_type,
                "data": base64_data
            }
        
        except Exception as e:
            logger.error(f"   ❌ Data URI parsing failed: {e}")
            raise
    
    def _aggregate_scores(self, results: List[Dict]) -> Dict:
        """
        Aggregate individual image analyses into overall design scores.
        
        Converts 0-6 per-image scale to 0-20 overall design scale.
        """
        
        if not results:
            return self._default_scores()
        
        # Aggregate by averaging
        dimensions = ['lighting', 'colors', 'clutter', 'staging', 'functionality']
        
        aggregates = {}
        for dim in dimensions:
            scores = [r.get(dim, 3) for r in results if dim in r]
            avg = sum(scores) / len(scores) if scores else 3
            # Convert 0-6 scale to 0-20 scale
            aggregates[dim] = int((avg / 6) * 20)
        
        # Collect strategic insights
        strategic_notes = []
        trust_signals = []
        for result in results:
            if result.get('strategic_notes'):
                strategic_notes.append(result['strategic_notes'])
            if result.get('trust_signal'):
                trust_signals.append(result['trust_signal'])
        
        # Room summaries
        room_summaries = {}
        for result in results:
            room = result.get('room_type', 'other')
            if room not in room_summaries:
                room_summaries[room] = {
                    'count': 0,
                    'avg_lighting': 0,
                    'avg_staging': 0,
                    'notes': [],
                    'strategic_notes': []
                }
            
            summary = room_summaries[room]
            summary['count'] += 1
            summary['avg_lighting'] += result.get('lighting', 3)
            summary['avg_staging'] += result.get('staging', 3)
            if result.get('notes'):
                summary['notes'].append(result['notes'])
            if result.get('strategic_notes'):
                summary['strategic_notes'].append(result['strategic_notes'])
        
        # Normalize room summaries
        for room, data in room_summaries.items():
            if data['count'] > 0:
                data['avg_lighting'] = int((data['avg_lighting'] / data['count'] / 6) * 20)
                data['avg_staging'] = int((data['avg_staging'] / data['count'] / 6) * 20)
        
        # Determine overall trust signal
        overall_trust = 'medium'
        if trust_signals:
            high_count = trust_signals.count('high')
            low_count = trust_signals.count('low')
            if high_count > len(trust_signals) / 2:
                overall_trust = 'high'
            elif low_count > len(trust_signals) / 2:
                overall_trust = 'low'
        
        # Build strategic narrative
        strategic_narrative = '. '.join(strategic_notes) if strategic_notes else 'Property analysis complete.'
        
        return {
            'lighting_quality': aggregates['lighting'],
            'color_harmony': aggregates['colors'],
            'clutter_density': aggregates['clutter'],
            'staging_integrity': aggregates['staging'],
            'functionality': aggregates['functionality'],
            'guest_psychology': strategic_narrative,
            'trust_signal': overall_trust,
            'strategic_insights': strategic_notes,
            'room_summaries': room_summaries
        }
    
    def _default_scores(self) -> Dict:
        """Return default scores when vision analysis unavailable"""
        return {
            'lighting_quality': 10,
            'color_harmony': 10,
            'clutter_density': 10,
            'staging_integrity': 10,
            'functionality': 10,
            'guest_psychology': 'Design analysis unavailable - using default assessment',
            'room_summaries': {},
            'raw_analyses': []
        }
