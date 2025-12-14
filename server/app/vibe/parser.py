"""
CSV parser for Vibe API data.
"""
import pandas as pd
import io
from typing import List, Dict
from app.core.logging import logger
from app.core.exceptions import ValidationError


class VibeParser:
    """Parser for Vibe API CSV responses."""
    
    REQUIRED_COLUMNS = [
        'date',
        'campaign_name',
        'strategy_name',
        'placement_name',
        'creative_name',
        'impressions',
        'clicks',
        'conversions',
        'revenue'
    ]
    
    @staticmethod
    def parse_csv(csv_content: bytes) -> List[Dict]:
        """
        Parse Vibe API CSV response.
        
        Args:
            csv_content: CSV content as bytes
            
        Returns:
            List of dictionaries (one per row)
            
        Raises:
            ValidationError: If CSV is invalid
        """
        try:
            # Read CSV from bytes
            df = pd.read_csv(io.BytesIO(csv_content))
            
            logger.info(f"Read {len(df)} rows from Vibe CSV")
            
            # Validate columns
            missing_columns = [col for col in VibeParser.REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(
                    f"Missing required columns in Vibe CSV: {', '.join(missing_columns)}"
                )
            
            # Clean data
            df = df.dropna(how='all')
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            logger.info(f"Parsed {len(records)} valid records from Vibe CSV")
            
            return records
            
        except pd.errors.EmptyDataError:
            raise ValidationError("CSV is empty")
        except pd.errors.ParserError as e:
            raise ValidationError(f"Error parsing CSV: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing Vibe CSV: {str(e)}")
            raise ValidationError(f"Failed to parse CSV: {str(e)}")
