"""
Vibe API HTTP client for async report workflow.
Based on official Vibe API documentation: https://help.vibe.co/en/articles/8943325-vibe-api-reporting
"""
import httpx
import asyncio
from typing import Dict, Optional, List
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
        
        # Async HTTP client with correct authentication header
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'X-API-KEY': self.api_key,
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
        url = f"{self.base_url}/rest/reporting/v1/create_async_report"
        
        # Map internal metrics to Vibe API metrics
        # Note: 'clicks' is not supported by Vibe API (CTV focus). 
        # 'conversions' -> 'number_of_purchases'
        # 'revenue' -> 'amount_of_purchases'
        
        payload = {
            'advertiser_id': self.advertiser_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'metrics': [
                'impressions',
                'spend',
                'number_of_purchases',  # conversions
                'amount_of_purchases',  # revenue
            ],
            'dimensions': [
                'campaign_name',
                'strategy_name',
                'creative_name'
                # 'date' is handled by granularity="day"
                # 'placement_name' is not supported by Vibe
            ],
            'filters': [],  # Required field
            'format': 'CSV',  # Required field
            'granularity': 'day'
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Created Vibe report: {data.get('report_id')}")
            
            return {
                'report_id': data.get('report_id'),
                'status': data.get('status', 'CREATED')
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
        url = f"{self.base_url}/rest/reporting/v1/get_report_status"
        params = {'report_id': report_id}
        
        try:
            response = await self.client.get(url, params=params)
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
            download_url: Pre-signed S3 URL to download report from
            
        Returns:
            CSV content as bytes
            
        Raises:
            VibeAPIError: If download fails
        """
        try:
            # Use a fresh client without auth headers since download_url is pre-signed
            async with httpx.AsyncClient() as client:
                response = await client.get(download_url)
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
        poll_interval: int = 10
    ) -> str:
        """
        Wait for report to be ready and return download URL.
        
        Args:
            report_id: Report UUID
            max_wait_seconds: Maximum time to wait (default 10 minutes)
            poll_interval: Seconds between status checks (default 10s)
            
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
            status = status_info.get('status')
            
            if status == 'DONE':
                logger.info(f"Report {report_id} is ready")
                return status_info['download_url']
            
            elif status == 'FAILED':
                error_msg = status_info.get('error_message', 'Unknown error')
                raise VibeAPIError(f"Report failed: {error_msg}")
            
            elif status in ['CREATED', 'PROCESSING']:
                logger.debug(f"Report {report_id} status: {status}, waiting {poll_interval}s...")
                await asyncio.sleep(poll_interval)
            
            else:
                raise VibeAPIError(f"Unknown report status: {status}")
    
    async def get_advertiser_ids(self) -> list:
        """
        Get list of advertisers.
        
        Returns:
            List of dictionaries with advertiser_id and advertiser_name
        """
        url = f"{self.base_url}/rest/reporting/v1/get_advertiser_ids"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Vibe API error: {e.response.status_code}")
            raise VibeAPIError(f"Failed to get advertisers: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting advertisers: {str(e)}")
            raise VibeAPIError(f"Failed to get advertisers: {str(e)}")

    async def get_app_ids(self, advertiser_id: str) -> list:
        """
        Get list of app IDs for an advertiser.
        
        Args:
            advertiser_id: Advertiser UUID
            
        Returns:
            List of app ID strings
        """
        url = f"{self.base_url}/rest/reporting/v1/get_app_ids"
        params = {'advertiser_id': advertiser_id}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('app_ids', [])
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Vibe API error: {e.response.status_code}")
            raise VibeAPIError(f"Failed to get app IDs: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting app IDs: {str(e)}")
            raise VibeAPIError(f"Failed to get app IDs: {str(e)}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
