"""
CSV/XLSX parser for Facebook upload data.
"""
import pandas as pd
from typing import List, Dict
from pathlib import Path
from app.core.logging import logger
from app.core.exceptions import ValidationError


class FacebookParser:
    """Parser for Facebook CSV/XLSX files."""
    
    REQUIRED_COLUMNS = [
        'Date',
        'Campaign Name',
        'Ad Set Name',
        'Ad Name',
        'Impressions',
        'Clicks',
        'Conversions',
        'Revenue'
    ]
    
    @staticmethod
    def validate_columns(df: pd.DataFrame):
        """Validate that all required columns are present."""
        missing_columns = [col for col in FacebookParser.REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Required columns: {', '.join(FacebookParser.REQUIRED_COLUMNS)}"
            )
    
    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        """
        Parse Facebook CSV or XLSX file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ValidationError: If file format is invalid or required columns are missing
        """
        try:
            path = Path(file_path)
            
            # Read file based on extension
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValidationError(f"Unsupported file format: {path.suffix}")
            
            # Validate columns
            FacebookParser.validate_columns(df)
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            logger.info(f"Successfully parsed {len(records)} records from Facebook file: {path.name}")
            
            return records
            
        except pd.errors.EmptyDataError:
            raise ValidationError("File is empty")
        except pd.errors.ParserError as e:
            raise ValidationError(f"Failed to parse file: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing Facebook file: {str(e)}")
            raise ValidationError(f"Error parsing file: {str(e)}")
