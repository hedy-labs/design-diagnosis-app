"""
Photo Scraper — Extract image URLs from Airbnb/VRBO listings

Uses Playwright with stealth plugin to bypass Cloudflare anti-bot detection.
Extracts direct image URLs for Vision AI analysis.
"""

import logging
import asyncio
import re
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


async def extract_airbnb_photos(listing_url: str) -> List[str]:
    """
    Extract image URLs from Airbnb listing using Playwright with stealth.
    
    Args:
        listing_url: Full Airbnb or VRBO listing URL
    
    Returns:
        List of direct image URLs (cloudinary or amazonaws CDN links)
    
    Raises:
        Exception: If scraping fails (network, timeout, invalid URL)
    """
    try:
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async
    except ImportError:
        logger.error("❌ playwright or playwright-stealth not installed")
        raise Exception("Scraper dependencies missing. Install: pip install playwright playwright-stealth")
    
    # Validate URL
    if not _is_valid_listing_url(listing_url):
        raise Exception(f"Invalid Airbnb/VRBO URL: {listing_url}")
    
    logger.info(f"🔍 Extracting photos from: {listing_url}")
    
    async with async_playwright() as p:
        # Launch browser with stealth
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Apply stealth modifications
        page = await context.new_page()
        await stealth_async(page)
        
        try:
            # Navigate to listing
            logger.info(f"📄 Loading listing page...")
            await page.goto(listing_url, wait_until="networkidle", timeout=30000)
            
            # Wait for images to load
            await asyncio.sleep(2)
            
            # Extract image URLs using multiple strategies
            image_urls = await _extract_image_urls(page, listing_url)
            
            if not image_urls:
                logger.warning(f"⚠️  No images found, attempting fallback extraction...")
                image_urls = await _extract_image_urls_fallback(page)
            
            logger.info(f"✅ Extracted {len(image_urls)} image URLs")
            return image_urls
        
        finally:
            await context.close()
            await browser.close()


async def _extract_image_urls(page, listing_url: str) -> List[str]:
    """
    Extract image URLs from Airbnb listing page.
    
    Tries multiple strategies to find image sources:
    1. data-testid attributes (Airbnb official)
    2. picture > source srcset
    3. img src attributes
    """
    
    try:
        # Strategy 1: Airbnb-specific data-testid
        logger.info("📸 Extracting via data-testid strategy...")
        images = await page.evaluate("""
            () => {
                const urls = [];
                // Look for images in carousels and photo grids
                document.querySelectorAll('[data-testid*="photo"], [role="img"]').forEach(el => {
                    if (el.src) urls.push(el.src);
                    else if (el.style.backgroundImage) {
                        const match = el.style.backgroundImage.match(/url\\("([^"]+)"\\)/);
                        if (match) urls.push(match[1]);
                    }
                });
                return urls;
            }
        """)
        
        if images:
            logger.info(f"   Found {len(images)} images via data-testid")
            return _clean_image_urls(images)
        
        # Strategy 2: Picture/source srcset (responsive images)
        logger.info("📸 Extracting via picture > source strategy...")
        images = await page.evaluate("""
            () => {
                const urls = [];
                document.querySelectorAll('picture source').forEach(source => {
                    const srcset = source.getAttribute('srcset');
                    if (srcset) {
                        srcset.split(',').forEach(item => {
                            const url = item.trim().split(' ')[0];
                            if (url) urls.push(url);
                        });
                    }
                });
                return urls;
            }
        """)
        
        if images:
            logger.info(f"   Found {len(images)} images via picture/source")
            return _clean_image_urls(images)
        
        # Strategy 3: All img tags with cdn domains
        logger.info("📸 Extracting via img tag strategy...")
        images = await page.evaluate("""
            () => {
                const urls = [];
                document.querySelectorAll('img[src*="airbnbnb"], img[src*="amazonaws"], img[src*="cloudinary"]').forEach(img => {
                    if (img.src) urls.push(img.src);
                });
                return urls;
            }
        """)
        
        if images:
            logger.info(f"   Found {len(images)} images via img tags")
            return _clean_image_urls(images)
        
        logger.warning("⚠️  No images found via standard strategies")
        return []
    
    except Exception as e:
        logger.error(f"❌ Error during image extraction: {e}")
        raise


async def _extract_image_urls_fallback(page) -> List[str]:
    """
    Fallback strategy: Extract all images from page HTML.
    Less precise but catches edge cases.
    """
    
    try:
        html = await page.content()
        
        # Find URLs that look like CDN image links
        patterns = [
            r'https://[^\s"\'<>]+(?:airbnbnb|cloudinary|amazonaws)[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)',
            r'https://[^\s"\'<>]+/images/[^\s"\'<>]+',
        ]
        
        all_images = set()
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            all_images.update(matches)
        
        if all_images:
            logger.info(f"   Fallback found {len(all_images)} potential image URLs")
            return list(all_images)[:40]  # Limit to 40
        
        return []
    
    except Exception as e:
        logger.error(f"❌ Fallback extraction failed: {e}")
        return []


def _clean_image_urls(urls: List[str]) -> List[str]:
    """
    Clean and deduplicate image URLs.
    Remove params, sort by quality, limit to 40 images.
    """
    
    cleaned = set()
    
    for url in urls:
        if not url or not isinstance(url, str):
            continue
        
        # Skip tracking pixels and small images
        if any(skip in url.lower() for skip in ['tracking', 'pixel', '1x1', 'transparent', 'data:']):
            continue
        
        # Remove quality/size params to get full-res URL
        base_url = url.split('?')[0]
        if base_url and len(base_url) > 20:
            cleaned.add(base_url)
    
    # Sort by domain (prefer direct CDN)
    sorted_urls = sorted(
        cleaned,
        key=lambda x: (
            'airbnbnb' not in x,  # Prefer airbnbnb first
            'amazonaws' not in x,
            'cloudinary' not in x
        )
    )
    
    # Return up to 40 images
    result = sorted_urls[:40]
    logger.info(f"✅ Cleaned {len(result)} unique image URLs (from {len(urls)} total)")
    return result


def _is_valid_listing_url(url: str) -> bool:
    """
    Validate that URL is a real Airbnb or VRBO listing.
    """
    
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # Check for Airbnb patterns
    if 'airbnb' in url_lower:
        return '/rooms/' in url_lower or '/listings/' in url_lower
    
    # Check for VRBO patterns
    if 'vrbo' in url_lower or 'homeaway' in url_lower:
        return '/listing' in url_lower or '/properties' in url_lower
    
    return False


def extract_airbnb_photos_sync(listing_url: str) -> List[str]:
    """
    Synchronous wrapper for async scraper (for use in FastAPI handlers).
    """
    
    try:
        # Check if event loop exists
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, use create_task
            raise RuntimeError("Use extract_airbnb_photos() directly in async context")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(extract_airbnb_photos(listing_url))
    except Exception as e:
        logger.error(f"❌ Photo extraction failed: {e}")
        raise
