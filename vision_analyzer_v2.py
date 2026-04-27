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
            tasks = [self._analyze_single_image(url) for url in sampled]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            valid_results = [r for r in results if isinstance(r, dict) and r.get('success')]
            failed = len([r for r in results if isinstance(r, Exception) or not r.get('success')])
            
            if failed > 0:
                logger.warning(f"⚠️  {failed} images failed to analyze")
            
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
        Analyze one image using Claude Vision API.
        
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
            
            message = client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "url",
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": """Analyze this Airbnb/VRBO interior for design quality.
                                Rate each on 0-6 scale (0=poor, 6=excellent):
                                
                                - Lighting Quality: brightness, color temp, shadows (warm/cool)
                                - Color Harmony: cohesive palette, professional taste, contrast
                                - Clutter Density: organized/clean (6) vs messy (0)
                                - Staging Integrity: professional decor (6) vs bare/neglected (0)
                                - Functionality: guest needs visible - seating, storage, workspace
                                - Room Type: kitchen, bedroom, bathroom, living, entry, storage, other
                                
                                Return ONLY valid JSON (no markdown):
                                {
                                    "lighting": 0-6,
                                    "colors": 0-6,
                                    "clutter": 0-6,
                                    "staging": 0-6,
                                    "functionality": 0-6,
                                    "room_type": "kitchen|bedroom|bathroom|living|entry|storage|other",
                                    "notes": "brief assessment"
                                }"""
                            }
                        ]
                    }
                ]
            )
            
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
            return result
        
        except Exception as e:
            logger.error(f"   ❌ Analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
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
        
        # Room summaries
        room_summaries = {}
        for result in results:
            room = result.get('room_type', 'other')
            if room not in room_summaries:
                room_summaries[room] = {
                    'count': 0,
                    'avg_lighting': 0,
                    'avg_staging': 0,
                    'notes': []
                }
            
            summary = room_summaries[room]
            summary['count'] += 1
            summary['avg_lighting'] += result.get('lighting', 3)
            summary['avg_staging'] += result.get('staging', 3)
            if result.get('notes'):
                summary['notes'].append(result['notes'])
        
        # Normalize room summaries
        for room, data in room_summaries.items():
            if data['count'] > 0:
                data['avg_lighting'] = int((data['avg_lighting'] / data['count'] / 6) * 20)
                data['avg_staging'] = int((data['avg_staging'] / data['count'] / 6) * 20)
        
        return {
            'lighting_quality': aggregates['lighting'],
            'color_harmony': aggregates['colors'],
            'clutter_density': aggregates['clutter'],
            'staging_integrity': aggregates['staging'],
            'functionality': aggregates['functionality'],
            'guest_psychology': 'Property is well-maintained and professionally styled' if aggregates['staging'] > 15 else 'Property needs staging improvements',
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
