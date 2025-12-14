"""
CSV/XLSX parser for Surfside data files.
"""
import pandas as pd
from typing import List, Dict
from pathlib import Path
from app.core.logging import logger
from app.core.exceptions import ValidationError


class SurfsideParser:
    """Parser for Surfside CSV/XLSX files."""
    
    REQUIRED_COLUMNS = [
        'Date',
        'Campaign',
        'Strategy',
        'Placement',
        'Creative',
        'Impressions',
        'Clicks',
        'Conversions',
        'Conversion Revenue'
    ]
    
    OPTIONAL_COLUMNS = ['CTR']
    
    @staticmethod
    def validate_columns(df: pd.DataFrame) -> None:
        """
        Validate that DataFrame has all required columns.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            ValidationError: If required columns are missing
        """
        missing_columns = [col for col in SurfsideParser.REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            raise ValidationError(
                f"Missing required columns in Surfside file: {', '.join(missing_columns)}"
            )
    
    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        """
        Parse Surfside CSV or XLSX file.
        
        Args:
            file_path: Path to CSV or XLSX file
            
        Returns:
            List of dictionaries (one per row)
            
        Raises:
            ValidationError: If file format is invalid or columns are missing
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        try:
            # Read file based on extension
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValidationError(f"Unsupported file format: {path.suffix}")
            
            logger.info(f"Read {len(df)} rows from {file_path}")
            
            # Validate columns
            SurfsideParser.validate_columns(df)
            
            # Clean data
            df = df.dropna(how='all')  # Remove completely empty rows
            
            # Fill missing optional columns with defaults
            for col in SurfsideParser.OPTIONAL_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            logger.info(f"Parsed {len(records)} valid records from Surfside file")
            
            return records
            
        except pd.errors.EmptyDataError:
            raise ValidationError("File is empty")
        except pd.errors.ParserError as e:
            raise ValidationError(f"Error parsing file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing Surfside file: {str(e)}")
            raise ValidationError(f"Failed to parse file: {str(e)}")
    
    @staticmethod
    def preview_file(file_path: str, num_rows: int = 5) -> Dict:
        """
        Get preview of file contents.
        
        Args:
            file_path: Path to file
            num_rows: Number of rows to preview
            
        Returns:
            Dictionary with preview information
        """
        try:
            records = SurfsideParser.parse_file(file_path)
            
            return {
                'total_rows': len(records),
                'columns': SurfsideParser.REQUIRED_COLUMNS + SurfsideParser.OPTIONAL_COLUMNS,
                'preview': records[:num_rows]
            }
        except Exception as e:
            logger.error(f"Error previewing file: {str(e)}")
            raise
