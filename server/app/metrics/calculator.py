"""
CPM-based metrics calculator.
"""
from decimal import Decimal
from typing import Optional
from app.core.logging import logger


class MetricsCalculator:
    """Calculate derived metrics from raw data."""
    
    @staticmethod
    def calculate_spend(impressions: int, cpm: Decimal) -> Decimal:
        """
        Calculate spend based on impressions and CPM.
        
        Formula: spend = (impressions / 1000) * CPM
        
        Args:
            impressions: Number of impressions
            cpm: Cost per thousand impressions
            
        Returns:
            Calculated spend
        """
        if impressions == 0 or cpm == 0:
            return Decimal('0.00')
        
        spend = (Decimal(impressions) / Decimal(1000)) * cpm
        return spend.quantize(Decimal('0.01'))
    
    @staticmethod
    def calculate_ctr(impressions: int, clicks: int) -> Decimal:
        """
        Calculate Click-Through Rate (CTR).
        
        Formula: CTR = (clicks / impressions) 
        
        Args:
            impressions: Number of impressions
            clicks: Number of clicks
            
        Returns:
            CTR or 0 if impressions is 0
        """
        if impressions == 0:
            return Decimal('0')
        
        ctr = (Decimal(clicks) / Decimal(impressions)) 
        return ctr.quantize(Decimal('0.000001'))
    
    @staticmethod
    def calculate_cpc(spend: Decimal, clicks: int) -> Decimal:
        """
        Calculate Cost Per Click (CPC).
        
        Formula: CPC = spend / clicks
        
        Args:
            spend: Total spend
            clicks: Number of clicks
            
        Returns:
            CPC or 0 if clicks is 0
        """
        if clicks == 0:
            return Decimal('0')
        
        cpc = spend / Decimal(clicks)
        return cpc.quantize(Decimal('0.0001'))
    
    @staticmethod
    def calculate_cpa(spend: Decimal, conversions: int) -> Decimal:
        """
        Calculate Cost Per Acquisition (CPA).
        
        Formula: CPA = spend / conversions
        
        Args:
            spend: Total spend
            conversions: Number of conversions
            
        Returns:
            CPA or 0 if conversions is 0
        """
        if conversions == 0:
            return Decimal('0')
        
        cpa = spend / Decimal(conversions)
        return cpa.quantize(Decimal('0.0001'))
    
    @staticmethod
    def calculate_roas(revenue: Decimal, spend: Decimal) -> Decimal:
        """
        Calculate Return on Ad Spend (ROAS).
        
        Formula: ROAS = revenue / spend
        
        Args:
            revenue: Total revenue from conversions
            spend: Total spend
            
        Returns:
            ROAS or 0 if spend is 0
        """
        if spend == 0:
            return Decimal('0')
        
        roas = revenue / spend
        return roas.quantize(Decimal('0.0001'))
    
    @staticmethod
    def calculate_all_metrics(
        impressions: int,
        clicks: int,
        conversions: int,
        revenue: Decimal,
        cpm: Decimal
    ) -> dict:
        """
        Calculate all metrics at once.
        
        Args:
            impressions: Number of impressions
            clicks: Number of clicks
            conversions: Number of conversions
            revenue: Total revenue
            cpm: Client CPM rate
            
        Returns:
            Dictionary with all calculated metrics
        """
        spend = MetricsCalculator.calculate_spend(impressions, cpm)
        
        return {
            'spend': spend,
            'ctr': MetricsCalculator.calculate_ctr(impressions, clicks),
            'cpc': MetricsCalculator.calculate_cpc(spend, clicks),
            'cpa': MetricsCalculator.calculate_cpa(spend, conversions),
            'roas': MetricsCalculator.calculate_roas(revenue, spend)
        }
