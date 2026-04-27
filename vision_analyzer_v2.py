"""
Vision Analyzer V2 — Batch Claude Vision Analysis for Property Photos

Analyzes multiple property photos in parallel, deduplicates by perceptual hash,
and aggregates design scores for vitality calculation.
"""

import logging
import asyncio
import json
import os
from typing import List, Dict, Optional
import imagehash
from PIL import Image
from io import BytesIO
import httpx

logger = logging.getLogger(__name__)


class VisionAnalyzerV2:
    """Batch vision analysis for property photos"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-3-5-sonnet-20241022"
    
    async def analyze_images_batch(self, image_urls: List[str], max_images: int = 10) -> Dict:
        """
        Analyze multiple property images in parallel using Claude Vision.
        
        Deduplicates images, samples best ones per room, analyzes in parallel.
        
        Args:
            image_urls: List of direct image URLs (from photo scraper)
            max_images: Max images to analyze (default 10)
        
        Returns:
            {
                'lighting_quality': 0-20,
                'color_harmony': 0-20,
                'clutter_density': 0-20,
                'staging_integrity': 0-20,
                'functionality': 0-20,
                'guest_psychology': str,
                'room_summaries': {'kitchen': {...}, 'bedroom': {...}, ...},
                'raw_analyses': [list of individual image analyses]
            }
        """
        
        if not image_urls:
            logger.warning("⚠️  No images provided, using default scores")
            return self._default_scores()
        
        try:
            # Smart sample images
            logger.info(f"📸 Deduplicating {len(image_urls)} images...")
            sampled = await self._smart_sample(image_urls, max_count=max_images)
            logger.info(f"✅ Sampled {len(sampled)} unique images for analysis")
            
            # Batch analyze in parallel
            logger.info(f"🤖 Analyzing {len(sampled)} images with Vision AI...")
            print(f"[VISION] 🤖 Starting batch analysis of {len(sampled)} images")
            tasks = [self._analyze_single_image(url) for url in sampled]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors and print details
            valid_results = [r for r in results if isinstance(r, dict) and r.get('success')]
            failed_results = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r.get('success'))]
            failed = len(failed_results)
            
            if failed > 0:
                print(f"[VISION] ⚠️  {failed} images FAILED in batch analysis:")
                for idx, result in enumerate(failed_results):
                    if isinstance(result, Exception):
                        print(f"[VISION]    Image {idx + 1}: Exception: {type(result).__name__}: {str(result)}")
                    elif isinstance(result, dict):
                        error_msg = result.get('error', 'Unknown error')
                        error_type = result.get('error_type', 'Unknown')
                        print(f"[VISION]    Image {idx + 1}: {error_type}: {error_msg}")
                logger.warning(f"⚠️  {failed} images failed to analyze")
                for result in failed_results:
                    if isinstance(result, dict):
                        logger.warning(f"      Error: {result.get('error')}")
            
            if not valid_results:
                logger.warning("⚠️  No successful vision analyses, using default scores")
                return self._default_scores()
            
            # Aggregate scores
            logger.info(f"📊 Aggregating {len(valid_results)} analyses...")
            aggregated = self._aggregate_scores(valid_results)
            aggregated['raw_analyses'] = valid_results
            
            logger.info(f"✅ Vision analysis complete")
            return aggregated
        
        except Exception as e:
            logger.error(f"❌ Batch analysis error: {e}")
            logger.info("📧 Falling back to default scores")
            return self._default_scores()
    
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
