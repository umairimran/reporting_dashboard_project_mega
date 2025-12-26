"""
Standalone script to test metrics calculation from CSV files.
Calculates all fields needed for daily_metrics table.

Usage:
    1. Configure parameters in the __main__ section
    2. Run: python test_metrics_calculator.py
"""
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path
import sys


class MetricsCalculator:
    """Calculate marketing metrics."""
    
    @staticmethod
    def calculate_spend(impressions: int, cpm: Decimal) -> Decimal:
        """
        Calculate spend based on impressions and CPM.
        Formula: Spend = (Impressions / 1,000) × CPM
        """
        if impressions == 0 or cpm == 0:
            return Decimal('0.00')
        
        spend = (Decimal(impressions) / Decimal(1000)) * cpm
        return spend.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_ctr(impressions: int, clicks: int) -> Decimal:
        """
        Calculate Click-Through Rate.
        Formula: CTR = (Clicks / Impressions) × 100
        """
        if impressions == 0:
            return Decimal('0.00')
        
        ctr = (Decimal(clicks) / Decimal(impressions)) * Decimal(100)
        return ctr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_cpc(spend: Decimal, clicks: int) -> Decimal:
        """
        Calculate Cost Per Click.
        Formula: CPC = Spend / Clicks
        """
        if clicks == 0:
            return Decimal('0.00')
        
        cpc = spend / Decimal(clicks)
        return cpc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_cpa(spend: Decimal, conversions: int) -> Decimal:
        """
        Calculate Cost Per Acquisition.
        Formula: CPA = Spend / Conversions
        """
        if conversions == 0:
            return Decimal('0.00')
        
        cpa = spend / Decimal(conversions)
        return cpa.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_roas(revenue: Decimal, spend: Decimal) -> Decimal:
        """
        Calculate Return on Ad Spend.
        Formula: ROAS = Revenue / Spend
        """
        if spend == 0:
            return Decimal('0.00')
        
        roas = revenue / spend
        return roas.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class CSVProcessor:
    """Process CSV files and calculate metrics."""
    
    # Column mappings for different sources
    SURFSIDE_COLUMNS = {
        'date': 'Event Date',
        'campaign_name': 'Strategy Name',  # Surfside uses Strategy as top level
        'strategy_name': 'Strategy Name',
        'placement_name': 'Placement Name',
        'creative_name': 'Creative Name',
        'impressions': 'Impressions',
        'clicks': 'Clicks',
        'conversions': 'Conversions',
        'conversion_revenue': 'Conversion Value'
    }
    
    VIBE_COLUMNS = {
        'date': 'impression_date',
        'campaign_name': 'campaign_name',
        'strategy_name': 'strategy_name',
        'placement_name': 'channel_name',  # Maps to placement
        'creative_name': 'creative_name',
        'impressions': 'impressions',
        'clicks': 'installs',  # Maps to clicks
        'conversions': 'number_of_purchases',  # Maps to conversions
        'conversion_revenue': 'amount_of_purchases'  # Maps to revenue
    }
    
    FACEBOOK_COLUMNS = {
        'date': 'date',
        'campaign_name': 'campaign_name',
        'strategy_name': 'ad_set_name',
        'placement_name': 'placement',
        'creative_name': 'ad_name',
        'impressions': 'impressions',
        'clicks': 'clicks',
        'conversions': 'conversions',
        'conversion_revenue': 'conversion_value'
    }
    
    def __init__(self, csv_path: str, source: str, cpm: Decimal):
        """
        Initialize processor.
        
        Args:
            csv_path: Path to CSV file
            source: Data source ('surfside', 'vibe', 'facebook')
            cpm: CPM value to use for calculations
        """
        self.csv_path = Path(csv_path)
        self.source = source.lower()
        self.cpm = Decimal(str(cpm))
        self.calculator = MetricsCalculator()
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        if self.source not in ['surfside', 'vibe', 'facebook']:
            raise ValueError(f"Invalid source: {source}. Must be 'surfside', 'vibe', or 'facebook'")
    
    def get_column_mapping(self):
        """Get column mapping for the source."""
        if self.source == 'surfside':
            return self.SURFSIDE_COLUMNS
        elif self.source == 'vibe':
            return self.VIBE_COLUMNS
        else:  # facebook
            return self.FACEBOOK_COLUMNS
    
    def parse_csv(self) -> pd.DataFrame:
        """Parse CSV and map columns."""
        print(f"\n{'='*80}")
        print(f"Reading CSV: {self.csv_path}")
        print(f"Source: {self.source}")
        print(f"CPM: ${self.cpm}")
        print(f"{'='*80}\n")
        
        # Read CSV
        df = pd.read_csv(self.csv_path)
        
        # Normalize column names
        df.columns = df.columns.str.strip()
        
        print(f"Original columns: {list(df.columns)}\n")
        
        # Get column mapping
        mapping = self.get_column_mapping()
        
        # Check for required columns
        missing_cols = []
        for target_col, source_col in mapping.items():
            if source_col not in df.columns:
                missing_cols.append(source_col)
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Rename columns
        reverse_mapping = {v: k for k, v in mapping.items()}
        df = df.rename(columns=reverse_mapping)
        
        # For Surfside, campaign_name and strategy_name map to same column
        # Create campaign_name if it doesn't exist
        if 'campaign_name' not in df.columns and 'strategy_name' in df.columns:
            df['campaign_name'] = df['strategy_name']
        
        # Drop rows with all NaN
        df = df.dropna(how='all')
        
        print(f"Mapped columns: {list(df.columns)}")
        print(f"Total rows: {len(df)}\n")
        
        return df
    
    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all metrics for each row."""
        print("Calculating metrics...")
        
        results = []
        
        for idx, row in df.iterrows():
            # Extract raw values
            impressions = int(row['impressions']) if pd.notna(row['impressions']) else 0
            clicks = int(row['clicks']) if pd.notna(row['clicks']) else 0
            conversions = int(row['conversions']) if pd.notna(row['conversions']) else 0
            revenue = Decimal(str(row['conversion_revenue'])) if pd.notna(row['conversion_revenue']) else Decimal('0.00')
            
            # Calculate derived metrics
            spend = self.calculator.calculate_spend(impressions, self.cpm)
            ctr = self.calculator.calculate_ctr(impressions, clicks)
            cpc = self.calculator.calculate_cpc(spend, clicks)
            cpa = self.calculator.calculate_cpa(spend, conversions)
            roas = self.calculator.calculate_roas(revenue, spend)
            
            # Build result row
            result = {
                'date': row['date'],
                'campaign_name': row['campaign_name'],
                'strategy_name': row['strategy_name'],
                'placement_name': row['placement_name'],
                'creative_name': row['creative_name'],
                'source': self.source,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'conversion_revenue': float(revenue),
                'cpm': float(self.cpm),
                'spend': float(spend),
                'ctr': float(ctr),
                'cpc': float(cpc),
                'cpa': float(cpa),
                'roas': float(roas)
            }
            
            results.append(result)
        
        results_df = pd.DataFrame(results)
        print(f"[OK] Calculated metrics for {len(results_df)} rows\n")
        
        return results_df
    
    def print_summary(self, df: pd.DataFrame):
        """Print summary statistics."""
        print(f"\n{'='*80}")
        print("SUMMARY STATISTICS")
        print(f"{'='*80}\n")
        
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_conversions = df['conversions'].sum()
        total_revenue = df['conversion_revenue'].sum()
        total_spend = df['spend'].sum()
        
        avg_ctr = self.calculator.calculate_ctr(int(total_impressions), int(total_clicks))
        avg_cpc = self.calculator.calculate_cpc(Decimal(str(total_spend)), int(total_clicks))
        avg_cpa = self.calculator.calculate_cpa(Decimal(str(total_spend)), int(total_conversions))
        total_roas = self.calculator.calculate_roas(Decimal(str(total_revenue)), Decimal(str(total_spend)))
        
        print(f"Source:              {self.source}")
        print(f"CPM:                 ${self.cpm}")
        print(f"Total Rows:          {len(df)}")
        print(f"\nRaw Metrics:")
        print(f"  Impressions:       {total_impressions:,}")
        print(f"  Clicks:            {total_clicks:,}")
        print(f"  Conversions:       {total_conversions:,}")
        print(f"  Revenue:           ${total_revenue:,.2f}")
        print(f"\nCalculated Metrics:")
        print(f"  Spend:             ${total_spend:,.2f}")
        print(f"  CTR:               {avg_ctr}%")
        print(f"  CPC:               ${avg_cpc}")
        print(f"  CPA:               ${avg_cpa}")
        print(f"  ROAS:              {total_roas}x")
        print(f"\n{'='*80}\n")
    
    def save_results(self, df: pd.DataFrame, output_path: str = None):
        """Save results to CSV."""
        if output_path is None:
            output_path = self.csv_path.parent / f"{self.csv_path.stem}_with_metrics.csv"
        
        df.to_csv(output_path, index=False)
        print(f"[OK] Results saved to: {output_path}\n")
    
    def process(self, save_output: bool = True):
        """
        Main processing method.
        
        Args:
            save_output: Whether to save results to CSV
        """
        try:
            # Parse CSV
            df = self.parse_csv()
            
            # Calculate metrics
            results_df = self.calculate_metrics(df)
            
            # Print summary
            self.print_summary(results_df)
            
            # Save results
            if save_output:
                self.save_results(results_df)
            
            return results_df
            
        except Exception as e:
            print(f"\nERROR: {str(e)}\n")
            raise


def main():
    """
    Main function - Configure parameters here.
    """
    # ============================================================================
    # CONFIGURATION - EDIT THESE PARAMETERS
    # ============================================================================
    
    # Path to your CSV file
    CSV_FILE = r"c:\Users\Public\Upwork_Umair_Shahzad\reporting_dashboard_project_mega\data\surfside.csv"
    
    # Data source: 'surfside', 'vibe', or 'facebook'
    SOURCE = "surfside"
    
    # CPM value (Cost Per Mille)
    CPM = 17.00
    
    # Whether to save results to a new CSV file
    SAVE_OUTPUT = True
    
    # ============================================================================
    # END CONFIGURATION
    # ============================================================================
    
    print("\n" + "="*80)
    print("METRICS CALCULATOR TEST SCRIPT")
    print("="*80)
    
    # Create processor
    processor = CSVProcessor(
        csv_path=CSV_FILE,
        source=SOURCE,
        cpm=CPM
    )
    
    # Process the file
    results = processor.process(save_output=SAVE_OUTPUT)
    
    print("[OK] Processing complete!\n")
    
    # Optionally display first few rows
    print("First 5 rows of results:")
    print(results.head().to_string(index=False))
    print()


if __name__ == "__main__":
    main()





