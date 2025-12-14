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
            # Remove commas and currency symbols
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '').strip()
            
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
        
        Args:
            raw_record: Raw record from Surfside CSV
            
        Returns:
            Transformed record
        """
        return {
            'date': TransformerService.parse_date(raw_record.get('Date')),
            'campaign_name': TransformerService.normalize_string(raw_record.get('Campaign', '')),
            'strategy_name': TransformerService.normalize_string(raw_record.get('Strategy', '')) or "General Strategy",
            'placement_name': TransformerService.normalize_string(raw_record.get('Placement', '')) or "General Placement",
            'creative_name': TransformerService.normalize_string(raw_record.get('Creative', '')) or "General Creative",
            'impressions': TransformerService.parse_number(raw_record.get('Impressions', 0)),
            'clicks': TransformerService.parse_number(raw_record.get('Clicks', 0)),
            'conversions': TransformerService.parse_number(raw_record.get('Conversions', 0)),
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('Conversion Revenue', 0)),
            'ctr': TransformerService.parse_decimal(raw_record.get('CTR', 0))
        }
    
    @staticmethod
    def transform_vibe_record(raw_record: Dict) -> Dict:
        """
        Transform Vibe API record to standard format.
        
        Args:
            raw_record: Raw record from Vibe API
            
        Returns:
            Transformed record
        """
        return {
            'date': TransformerService.parse_date(raw_record.get('date')),
            'campaign_name': TransformerService.normalize_string(raw_record.get('campaign_name', '')),
            'strategy_name': TransformerService.normalize_string(raw_record.get('strategy_name', '')) or "General Strategy",
            'placement_name': TransformerService.normalize_string(raw_record.get('placement_name', '')) or "General Placement",
            'creative_name': TransformerService.normalize_string(raw_record.get('creative_name', '')) or "General Creative",
            'impressions': TransformerService.parse_number(raw_record.get('impressions', 0)),
            'clicks': TransformerService.parse_number(raw_record.get('clicks', 0)),
            'conversions': TransformerService.parse_number(raw_record.get('conversions', 0)),
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('revenue', 0)),
            'ctr': None  # Will be calculated
        }
    
    @staticmethod
    def transform_facebook_record(raw_record: Dict) -> Dict:
        """
        Transform Facebook upload record to standard format.
        
        Facebook structure: Campaign Name, Ad Set Name, Ad Name
        Mapping: Campaign Name → Campaign, Ad Set Name → Strategy, Ad Name → Placement + Creative
        
        Args:
            raw_record: Raw record from Facebook upload
            
        Returns:
            Transformed record
        """
        ad_name = TransformerService.normalize_string(raw_record.get('Ad Name', ''))
        
        # Split Ad Name into Placement and Creative (use first part as placement, full name as creative)
        placement_name = ad_name.split('-')[0].strip() if '-' in ad_name else ad_name
        creative_name = ad_name
        
        return {
            'date': TransformerService.parse_date(raw_record.get('Date')),
            'campaign_name': TransformerService.normalize_string(raw_record.get('Campaign Name', '')),
            'strategy_name': TransformerService.normalize_string(raw_record.get('Ad Set Name', '')) or "General Strategy",
            'placement_name': placement_name or "General Placement",
            'creative_name': creative_name or "General Creative",
            'impressions': TransformerService.parse_number(raw_record.get('Impressions', 0)),
            'clicks': TransformerService.parse_number(raw_record.get('Clicks', 0)),
            'conversions': TransformerService.parse_number(raw_record.get('Conversions', 0)),
            'conversion_revenue': TransformerService.parse_decimal(raw_record.get('Revenue', 0)),
            'ctr': None  # Will be calculated
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
