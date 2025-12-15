"""
Data transformation service for ETL pipeline.
"""
import re
from typing import Dict, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from app.core.logging import logger
from app.core.exceptions import ValidationError


class TransformerService:
    """Service for transforming and validating raw data."""
    
    @staticmethod
    def normalize_string(value: str) -> str:
        """
        Normalize string values (trim, clean special characters).
        
        Args:
            value: Raw string value
            
        Returns:
            Normalized string
        """
        if not value:
            return ""
        
        # Strip whitespace
        normalized = str(value).strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    @staticmethod
    def parse_date(value) -> date:
        """
        Parse date from various formats.
        
        Args:
            value: Date value (string or date object)
            
        Returns:
            Parsed date
            
        Raises:
            ValidationError: If date cannot be parsed
        """
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            
            raise ValidationError(f"Unable to parse date: {value}")
        
        raise ValidationError(f"Invalid date type: {type(value)}")
    
    @staticmethod
    def parse_number(value, default=0) -> int:
        """
        Parse integer from string or number.
        
        Args:
            value: Value to parse
            default: Default value if parsing fails
            
        Returns:
            Parsed integer
        """
        if value is None or value == '':
            return default
        
        try:
            # Remove commas and whitespace
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            
            return int(float(value))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse number: {value}, using default {default}")
            return default
    
    @staticmethod
    def parse_decimal(value, default=0.0) -> Decimal:
        """
        Parse decimal from string or number.
        
        Args:
            value: Value to parse
            default: Default value if parsing fails
            
        Returns:
            Parsed decimal
        """
        if value is None or value == '':
            return Decimal(str(default))
        
        try:
            # Remove commas, currency symbols, and extra whitespace
            if isinstance(value, str):
                # Handle special cases like "$ -" or just "-" for zero
                value = value.strip()
                if value in ['-', '$ -', '$-']:
                    return Decimal('0')
                
                # Remove currency symbols and commas
                value = value.replace(',', '').replace('$', '').strip()
                
                # Handle empty string after cleaning
                if not value or value == '-':
                    return Decimal('0')
            
            return Decimal(str(value))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse decimal: {value}, using default {default}")
            return Decimal(str(default))
    
    @staticmethod
    def validate_record(record: Dict, required_fields: List[str]) -> Tuple[bool, str]:
        """
        Validate that record has all required fields.
        
        Args:
            record: Record to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in record or record[field] is None or record[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, ""
    
    @staticmethod
    def transform_surfside_record(raw_record: Dict) -> Dict:
        """
        Transform Surfside raw record to standard format.
        
        Surfside Structure:
        - Event Date → date
        - Strategy Name → both campaign_name and strategy_name (no separate Campaign column)
        - Placement Name → placement_name
        - Creative Name → creative_name
        - Conversion Value → conversion_revenue
        - Media Spend → available but not used (we calculate spend from impressions * CPM)
        
        Args:
            raw_record: Raw record from Surfside CSV (with actual column names)
            
        Returns:
            Transformed record
        """
        strategy_name = TransformerService.normalize_string(raw_record.get('Strategy Name', ''))
        
        impressions = TransformerService.parse_number(raw_record.get('Impressions', 0))
        clicks = TransformerService.parse_number(raw_record.get('Clicks', 0))
        
        # Calculate CTR: (Clicks / Impressions) * 100
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        return {
            'date': TransformerService.parse_date(raw_record.get('Event Date')),
            'campaign_name': strategy_name or "Surfside Campaign",  # Use Strategy Name as Campaign
            'strategy_name': strategy_name or "General Strategy",
            'placement_name': TransformerService.normalize_string(raw_record.get('Placement Name', '')) or "General Placement",
            'creative_name': TransformerService.normalize_string(raw_record.get('Creative Name', '')) or "General Creative",
            'impressions': impressions,
            'clicks': clicks,
            'conversions': TransformerService.parse_number(raw_record.get('Conversions', 0)),
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('Conversion Value', 0)),
            'ctr': ctr
        }
    
    @staticmethod
    def transform_vibe_record(raw_record: Dict) -> Dict:
        """
        Transform Vibe API record to standard format.
        
        Vibe API Column Mappings:
        - impression_date → date
        - campaign_name → campaign_name
        - strategy_name → strategy_name  
        - channel_name → placement_name (MAPPED)
        - creative_name → creative_name
        - impressions → impressions
        - installs → clicks (MAPPED)
        - number_of_purchases → conversions (MAPPED)
        - amount_of_purchases → revenue/conversion_revenue (MAPPED)
        
        Args:
            raw_record: Raw record from Vibe API (with lowercase column names)
            
        Returns:
            Transformed record
        """
        impressions = TransformerService.parse_number(raw_record.get('impressions', 0))
        clicks = TransformerService.parse_number(raw_record.get('installs', 0))  # Vibe: installs → clicks
        
        # Calculate CTR: (Clicks / Impressions) * 100
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        return {
            'date': TransformerService.parse_date(raw_record.get('impression_date')),
            'campaign_name': TransformerService.normalize_string(raw_record.get('campaign_name', '')),
            'strategy_name': TransformerService.normalize_string(raw_record.get('strategy_name', '')) or "General Strategy",
            'placement_name': TransformerService.normalize_string(raw_record.get('channel_name', '')) or "General Placement",  # Vibe: channel_name → placement_name
            'creative_name': TransformerService.normalize_string(raw_record.get('creative_name', '')) or "General Creative",
            'impressions': impressions,
            'clicks': clicks,  # Vibe: installs → clicks
            'conversions': TransformerService.parse_number(raw_record.get('number_of_purchases', 0)),  # Vibe: number_of_purchases → conversions
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('amount_of_purchases', 0)),  # Vibe: amount_of_purchases → revenue
            'ctr': ctr
        }
    
    @staticmethod
    def transform_facebook_record(raw_record: Dict) -> Dict:
        """
        Transform Facebook upload record to standard format.
        
        Facebook structure: Campaign name, Ad set name, Ad name
        Mapping: Campaign name → Campaign, Ad set name → Strategy, Ad name → Placement + Creative
        
        Note: Column names are expected to be lowercase (normalized by parser)
        Regional data is handled by appending region to placement name for differentiation.
        
        Args:
            raw_record: Raw record from Facebook upload (with lowercase column names)
            
        Returns:
            Transformed record
        """
        ad_name = TransformerService.normalize_string(raw_record.get('ad name', ''))
        campaign_name = TransformerService.normalize_string(raw_record.get('campaign name', ''))
        ad_set_name = TransformerService.normalize_string(raw_record.get('ad set name', ''))
        region = TransformerService.normalize_string(raw_record.get('region', ''))
        
        # Use Ad name for both placement and creative
        # If region exists and is not 'Unknown', append to placement for differentiation
        placement_name = ad_name
        if region and region.lower() not in ['unknown', '']:
            placement_name = f"{ad_name} - {region}"
        
        creative_name = ad_name
        
        impressions = TransformerService.parse_number(raw_record.get('impressions', 0))
        # TODO: Clicks field - awaiting client confirmation (link clicks vs clicks (all))
        clicks = TransformerService.parse_number(raw_record.get('link clicks', 0))
        # clicks = TransformerService.parse_number(raw_record.get('clicks (all)', 0))  # Alternative
        
        # Calculate CTR: (Clicks / Impressions) * 100
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        return {
            # TODO: Date field - awaiting client confirmation on which field to use
            'date': TransformerService.parse_date(raw_record.get('reporting starts')),
            # 'date': TransformerService.parse_date(raw_record.get('reporting ends')),  # Alternative
            
            'campaign_name': campaign_name,
            'strategy_name': ad_set_name or "General Strategy",
            'placement_name': placement_name or "General Placement",
            'creative_name': creative_name or "General Creative",
            'impressions': impressions,
            'clicks': clicks,
            
            # TODO: Conversions - not in current CSV, awaiting client confirmation
            'conversions': TransformerService.parse_number(raw_record.get('conversions', 0)),
            
            # TODO: Revenue - not in current CSV, awaiting client confirmation
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('revenue', 0)),
            'ctr': ctr
        }
    
    @staticmethod
    def validate_and_transform(
        records: List[Dict],
        source: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate and transform all records.
        
        Args:
            records: List of raw records
            source: Data source ('surfside', 'vibe', 'facebook')
            
        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid_records = []
        invalid_records = []
        
        # Select transformation function based on source
        transform_func = {
            'surfside': TransformerService.transform_surfside_record,
            'vibe': TransformerService.transform_vibe_record,
            'facebook': TransformerService.transform_facebook_record
        }.get(source)
        
        if not transform_func:
            raise ValidationError(f"Unknown source: {source}")
        
        required_fields = ['date', 'campaign_name', 'strategy_name', 'placement_name', 'creative_name']
        
        for idx, raw_record in enumerate(records):
            try:
                # Transform record
                transformed = transform_func(raw_record)
                
                # Validate required fields
                is_valid, error_msg = TransformerService.validate_record(transformed, required_fields)
                
                if is_valid:
                    valid_records.append(transformed)
                else:
                    invalid_records.append({
                        'record_index': idx,
                        'error': error_msg,
                        'raw_data': raw_record
                    })
            
            except Exception as e:
                logger.error(f"Error transforming record {idx}: {str(e)}")
                invalid_records.append({
                    'record_index': idx,
                    'error': str(e),
                    'raw_data': raw_record
                })
        
        logger.info(f"Transformed {len(valid_records)} valid records, {len(invalid_records)} invalid records")
        
        return valid_records, invalid_records
    
    @staticmethod
    def aggregate_records(records: List[Dict]) -> List[Dict]:
        """
        Aggregate records that have the same dimension keys (date, campaign, strategy, placement, creative).
        This is necessary for sources like Surfside that provide multiple rows for the same dimensions
        (e.g., different creative sizes).
        
        Args:
            records: List of transformed records
            
        Returns:
            List of aggregated records with summed metrics
        """
        from collections import defaultdict
        from decimal import Decimal
        
        # Group records by dimension keys
        aggregated = defaultdict(lambda: {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'conversion_revenue': Decimal('0')
        })
        
        for record in records:
            # Create dimension key
            key = (
                str(record['date']),
                record['campaign_name'],
                record['strategy_name'],
                record['placement_name'],
                record['creative_name']
            )
            
            # Aggregate metrics
            aggregated[key]['impressions'] += record['impressions']
            aggregated[key]['clicks'] += record['clicks']
            aggregated[key]['conversions'] += record['conversions']
            aggregated[key]['conversion_revenue'] += record['conversion_revenue']
            
            # Store dimension values (same for all records with this key)
            aggregated[key]['date'] = record['date']
            aggregated[key]['campaign_name'] = record['campaign_name']
            aggregated[key]['strategy_name'] = record['strategy_name']
            aggregated[key]['placement_name'] = record['placement_name']
            aggregated[key]['creative_name'] = record['creative_name']
            aggregated[key]['ctr'] = None  # Will be recalculated
        
        # Convert back to list
        result = list(aggregated.values())
        
        logger.info(f"Aggregated {len(records)} records into {len(result)} unique dimension combinations")
        
        return result
