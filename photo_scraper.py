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
        ModuleNotFoundError: If playwright or playwright-stealth not installed
        ImportError: If other required modules missing
    """
    # Let native import errors propagate (don't wrap in custom Exception)
    from playwright.async_api import async_playwright
    from playwright_stealth import stealth_async
    
    # Validate URL
    if not _is_valid_listing_url(listing_url):
        print(f"[SCRAPER] ❌ Invalid URL format: {listing_url}")
        raise ValueError(f"Invalid Airbnb/VRBO URL: {listing_url}")
    
    print(f"[SCRAPER] 🔍 Starting extraction from: {listing_url}")
    logger.info(f"🔍 Extracting photos from: {listing_url}")
    
    try:
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
                logger.info(f"📄 Loading listing page: {listing_url}")
                print(f"[SCRAPER] 🔍 Navigating to: {listing_url}")
                
                try:
                    # Try with longer timeout (60s) for international domains
                    print(f"[SCRAPER] ⏳ Starting page load (60s timeout)...")
                    await page.goto(listing_url, wait_until="networkidle", timeout=60000)
                    print(f"[SCRAPER] ✅ Page loaded, networkidle reached")
                    logger.info(f"✅ Page loaded successfully")
                except Exception as nav_error:
                    print(f"[SCRAPER] ❌ Page load failed: {type(nav_error).__name__}: {nav_error}")
                    logger.error(f"❌ Page navigation failed: {nav_error}")
                    logger.info(f"   URL: {listing_url}")
                    logger.info(f"   Error type: {type(nav_error).__name__}")
                    raise
                
                # Wait for React to fully render images (international domains can be slower)
                print(f"[SCRAPER] ⏳ Waiting 5s for React image rendering...")
                await asyncio.sleep(5)
                print(f"[SCRAPER] ✅ React render wait complete")
                logger.info(f"⏳ Waited for images to render")
                
                # Check page title to verify we're on the right page
                title = await page.title()
                print(f"[SCRAPER] 📄 Page title: {title}")
                logger.info(f"📄 Page title: {title}")
                
                # Extract image URLs using multiple strategies
                print(f"[SCRAPER] 🔎 Starting image extraction (4 strategies)...")
                logger.info(f"🔎 Strategy 1: Extracting via data-testid...")
                print(f"[SCRAPER] 📸 Strategy 1: data-testid extraction...")
                image_urls = await _extract_image_urls(page, listing_url)
                
                if not image_urls:
                    logger.warning(f"⚠️  Strategy 1 failed, attempting fallback extraction...")
                    logger.info(f"🔎 Strategy 2: Regex-based extraction...")
                    image_urls = await _extract_image_urls_fallback(page)
                
                if image_urls:
                    print(f"[SCRAPER] ✅ SUCCESS: Extracted {len(image_urls)} image URLs")
                    logger.info(f"✅ Extracted {len(image_urls)} image URLs")
                else:
                    print(f"[SCRAPER] ❌ FAILURE: No image URLs found after all 4 strategies")
                    print(f"[SCRAPER] 📄 Final page URL: {page.url}")
                    print(f"[SCRAPER] 📄 Final page title: {title}")
                    logger.error(f"❌ No image URLs found after all strategies")
                    logger.info(f"   Page URL: {page.url}")
                    logger.info(f"   Page title: {title}")
                
                return image_urls
            
            except Exception as e:
                print(f"[SCRAPER] ❌ CRITICAL SCRAPER ERROR (in extraction block)")
                print(f"[SCRAPER]    Exception type: {type(e).__name__}")
                print(f"[SCRAPER]    Error message: {str(e)}")
                import traceback
                print(f"[SCRAPER]    Traceback:")
                for line in traceback.format_exc().split('\n'):
                    if line:
                        print(f"[SCRAPER]      {line}")
                logger.error(f"❌ Scraper fatal error: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                logger.error(f"   URL: {listing_url}")
                logger.error(traceback.format_exc())
                raise
            
            finally:
                try:
                    await context.close()
                    await browser.close()
                    logger.info(f"✅ Browser closed cleanly")
                except Exception as close_error:
                    print(f"[SCRAPER] ⚠️  Browser close error: {type(close_error).__name__}: {close_error}")
                    logger.warning(f"⚠️  Browser close error: {close_error}")
    
    except (ModuleNotFoundError, ImportError) as import_err:
        print(f"[SCRAPER] ❌ IMPORT ERROR (dependency missing)")
        print(f"[SCRAPER]    Module: {import_err.__name__}")
        print(f"[SCRAPER]    Message: {str(import_err)}")
        logger.error(f"❌ Import error: {import_err}")
        raise
    except Exception as e:
        print(f"[SCRAPER] ❌ FATAL ERROR (top-level exception)")
        print(f"[SCRAPER]    Exception type: {type(e).__name__}")
        print(f"[SCRAPER]    Error message: {str(e)}")
        import traceback
        print(f"[SCRAPER]    Traceback:")
        for line in traceback.format_exc().split('\n'):
            if line:
                print(f"[SCRAPER]      {line}")
        logger.error(f"❌ Fatal scraper error: {e}")
        logger.error(traceback.format_exc())
        raise


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
        print(f"[SCRAPER] 📸 [Strategy 1] data-testid extraction...")
        logger.info("📸 Extracting via data-testid strategy...")
        try:
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
        except Exception as e:
            print(f"[SCRAPER] ❌ [Strategy 1] JS evaluation failed: {e}")
            images = []
        
        if images:
            print(f"[SCRAPER] ✅ [Strategy 1] Found {len(images)} images")
            logger.info(f"   Found {len(images)} images via data-testid")
            return _clean_image_urls(images)
        else:
            print(f"[SCRAPER] ⏭️  [Strategy 1] No images found, trying next strategy")
        
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
        
        # Strategy 4: Catch-all - all img tags on page (last resort)
        logger.info("📸 Extracting via catch-all img strategy...")
        images = await page.evaluate("""
            () => {
                const urls = [];
                document.querySelectorAll('img').forEach(img => {
                    if (img.src && (img.src.includes('airbnbnb') || img.src.includes('amazonaws') || img.src.includes('cloudinary'))) {
                        urls.push(img.src);
                    }
                });
                return urls;
            }
        """)
        
        if images:
            logger.info(f"   Found {len(images)} images via catch-all")
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
