"""
Email List Management Routes

Private dashboard for exporting opted-in users.
Includes CSV export and Mailchimp integration (stub for later activation).
"""

import logging
import csv
import io
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


def create_email_list_router(db):
    """Create email list management routes"""
    router = APIRouter(prefix="/api/email-list", tags=["email-list"])
    
    @router.get("/opted-in")
    async def get_opted_in_users(api_key: str = Query(...)):
        """
        Get list of all users who opted in to marketing emails.
        
        Requires API key for security (prevents unauthorized access).
        
        Query params:
        - api_key: Secret API key (set in .env as ADMIN_API_KEY)
        """
        try:
            from os import getenv
            admin_key = getenv("ADMIN_API_KEY", "")
            
            if not admin_key or api_key != admin_key:
                logger.warning(f"⚠️  Unauthorized email list access attempt with key: {api_key[:8]}...")
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            # Get opted-in emails
            emails = db.get_marketing_opted_in_emails()
            
            logger.info(f"✅ Email list accessed: {len(emails)} opted-in users")
            
            return {
                "success": True,
                "count": len(emails),
                "emails": emails,
                "exported_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Email list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/export-csv")
    async def export_opted_in_csv(api_key: str = Query(...)):
        """
        Export opted-in users as CSV file.
        
        Returns: CSV file download with email list
        """
        try:
            from os import getenv
            admin_key = getenv("ADMIN_API_KEY", "")
            
            if not admin_key or api_key != admin_key:
                logger.warning(f"⚠️  Unauthorized CSV export attempt")
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            # Get opted-in emails
            emails = db.get_marketing_opted_in_emails()
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["Email", "Exported Date"])
            
            # Data rows
            export_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            for email in emails:
                writer.writerow([email, export_date])
            
            # Convert to bytes
            csv_bytes = io.BytesIO(output.getvalue().encode())
            
            logger.info(f"✅ CSV export created: {len(emails)} emails")
            
            return StreamingResponse(
                iter([csv_bytes.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=opted_in_emails_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"}
            )
        
        except Exception as e:
            logger.error(f"❌ CSV export error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/mailchimp/sync")
    async def sync_to_mailchimp(api_key: str = Query(...)):
        """
        Sync opted-in users to Mailchimp audience.
        
        STUB: Currently returns "not configured"
        Will activate when Mailchimp API key is added to .env
        
        Requires:
        - MAILCHIMP_API_KEY in .env
        - MAILCHIMP_AUDIENCE_ID in .env
        """
        try:
            from os import getenv
            admin_key = getenv("ADMIN_API_KEY", "")
            
            if not admin_key or api_key != admin_key:
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            mailchimp_key = getenv("MAILCHIMP_API_KEY", "")
            mailchimp_audience = getenv("MAILCHIMP_AUDIENCE_ID", "")
            
            if not mailchimp_key or not mailchimp_audience:
                logger.warning("⚠️  Mailchimp not configured yet")
                return {
                    "success": False,
                    "message": "Mailchimp not configured. Add MAILCHIMP_API_KEY and MAILCHIMP_AUDIENCE_ID to .env to enable sync.",
                    "status": "not_configured"
                }
            
            # TODO: Implement Mailchimp sync
            # This would use mailchimp3 library to add emails to audience
            
            logger.info("✅ Mailchimp sync would happen here (stub)")
            
            return {
                "success": True,
                "message": "Mailchimp sync enabled (implementation pending)",
                "status": "ready"
            }
        
        except Exception as e:
            logger.error(f"❌ Mailchimp sync error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
