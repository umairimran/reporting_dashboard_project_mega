"""
Vibe API HTTP client for async report workflow.
"""
import httpx
import asyncio
from typing import Dict, Optional
from datetime import datetime, date
import uuid
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import VibeAPIError


class VibeAPIClient:
    """HTTP client for Vibe API with async report support."""
    
    def __init__(self, api_key: str, advertiser_id: Optional[str] = None):
        """
        Initialize Vibe API client.
        
        Args:
            api_key: Vibe API key
            advertiser_id: Optional advertiser ID
        """
        self.api_key = api_key or settings.VIBE_API_KEY
        self.advertiser_id = advertiser_id or settings.VIBE_ADVERTISER_ID
        self.base_url = settings.VIBE_API_BASE_URL
        self.rate_limit_per_hour = settings.VIBE_RATE_LIMIT_PER_HOUR
        
        # Async HTTP client
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
    
    async def create_report(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Create a new report request (async operation).
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dictionary with report_id and status
            
        Raises:
            VibeAPIError: If API request fails
        """
        url = f"{self.base_url}/reporting/v1/std/reports"
        
        payload = {
            'advertiser_id': self.advertiser_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'metrics': [
                'impressions',
                'clicks',
                'conversions',
                'revenue'
            ],
            'dimensions': [
                'date',
                'campaign_name',
                'strategy_name',
                'placement_name',
                'creative_name'
            ]
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Created Vibe report: {data.get('report_id')}")
            
            return {
                'report_id': data.get('report_id'),
                'status': data.get('status', 'created')
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Vibe API error: {e.response.status_code} - {e.response.text}")
            raise VibeAPIError(f"Failed to create report: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating Vibe report: {str(e)}")
            raise VibeAPIError(f"Failed to create report: {str(e)}")
    
    async def check_report_status(self, report_id: str) -> Dict:
        """
        Check status of a report request.
        
        Args:
            report_id: Report UUID
            
        Returns:
            Dictionary with status and download_url (if ready)
            
        Raises:
            VibeAPIError: If API request fails
        """
        url = f"{self.base_url}/reporting/v1/std/reports/{report_id}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'status': data.get('status'),
                'download_url': data.get('download_url'),
                'error_message': data.get('error_message')
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Vibe API error: {e.response.status_code}")
            raise VibeAPIError(f"Failed to check report status: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error checking report status: {str(e)}")
            raise VibeAPIError(f"Failed to check report status: {str(e)}")
    
    async def download_report(self, download_url: str) -> bytes:
        """
        Download report CSV from download URL.
        
        Args:
            download_url: URL to download report from
            
        Returns:
            CSV content as bytes
            
        Raises:
            VibeAPIError: If download fails
        """
        try:
            response = await self.client.get(download_url)
            response.raise_for_status()
            
            logger.info(f"Downloaded report CSV ({len(response.content)} bytes)")
            return response.content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to download report: {e.response.status_code}")
            raise VibeAPIError(f"Failed to download report: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error downloading report: {str(e)}")
            raise VibeAPIError(f"Failed to download report: {str(e)}")
    
    async def wait_for_report(
        self,
        report_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 30
    ) -> str:
        """
        Wait for report to be ready and return download URL.
        
        Args:
            report_id: Report UUID
            max_wait_seconds: Maximum time to wait (default 10 minutes)
            poll_interval: Seconds between status checks
            
        Returns:
            Download URL when report is ready
            
        Raises:
            VibeAPIError: If report fails or timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if we've exceeded max wait time
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait_seconds:
                raise VibeAPIError(f"Report timeout after {max_wait_seconds} seconds")
            
            # Check report status
            status_info = await self.check_report_status(report_id)
            status = status_info['status']
            
            if status == 'done':
                logger.info(f"Report {report_id} is ready")
                return status_info['download_url']
            
            elif status == 'failed':
                error_msg = status_info.get('error_message', 'Unknown error')
                raise VibeAPIError(f"Report failed: {error_msg}")
            
            elif status in ['created', 'processing']:
                logger.debug(f"Report {report_id} status: {status}, waiting...")
                await asyncio.sleep(poll_interval)
            
            else:
                raise VibeAPIError(f"Unknown report status: {status}")
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
