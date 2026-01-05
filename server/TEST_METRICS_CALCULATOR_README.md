# Metrics Calculator Testing Script

## Overview

This standalone script processes CSV files from different data sources (Surfside, Vibe, Facebook) and calculates all metrics needed for the `daily_metrics` table.

**Purpose**: Test and validate metric calculations before loading data into the database.

## Features

- ✅ Parses CSV files from multiple sources
- ✅ Applies custom CPM rates
- ✅ Calculates all derived metrics (Spend, CTR, CPC, CPA, ROAS)
- ✅ Provides detailed summary statistics
- ✅ Exports results to CSV with all calculated fields
- ✅ No database connection required

## Quick Start

### 1. Edit Parameters

Open `test_metrics_calculator.py` and edit the configuration section:

```python
# CONFIGURATION - EDIT THESE PARAMETERS
# ============================================================================

# Path to your CSV file
CSV_FILE = r"c:\path\to\your\file.csv"

# Data source: 'surfside', 'vibe', or 'facebook'
SOURCE = "surfside"

# CPM value (Cost Per Mille)
CPM = 17.00

# Whether to save results to a new CSV file
SAVE_OUTPUT = True
```

### 2. Run the Script

```bash
cd server
python test_metrics_calculator.py
```

Or with virtual environment:

```bash
C:\Users\Public\Upwork_Umair_Shahzad\reporting_dashboard_project_mega\venv\Scripts\python.exe test_metrics_calculator.py
```

## Supported Sources

### Surfside

**Expected columns:**
- Event Date
- Strategy Name
- Placement Name
- Creative Name
- Impressions
- Clicks
- Conversions
- Conversion Value

### Vibe

**Expected columns:**
- impression_date
- campaign_name
- strategy_name
- channel_name (maps to placement)
- creative_name
- impressions
- installs (maps to clicks)
- number_of_purchases (maps to conversions)
- amount_of_purchases (maps to revenue)

### Facebook

**Expected columns:**
- date
- campaign_name
- ad_set_name (maps to strategy)
- placement
- ad_name (maps to creative)
- impressions
- clicks
- conversions
- conversion_value

## Output

### Console Output

Shows:
1. File parsing details
2. Column mapping confirmation
3. Processing progress
4. **Summary statistics** including:
   - Total impressions, clicks, conversions, revenue
   - Calculated spend, CTR, CPC, CPA, ROAS
5. First 5 rows of results

### CSV Output

Creates a new file: `{original_filename}_with_metrics.csv`

**Output columns:**
- `date` - Date of record
- `campaign_name` - Campaign name
- `strategy_name` - Strategy/ad set name
- `placement_name` - Placement name
- `creative_name` - Creative/ad name
- `source` - Data source
- `impressions` - Raw impressions count
- `clicks` - Raw clicks count
- `conversions` - Raw conversions count
- `conversion_revenue` - Raw revenue value
- `cpm` - CPM used for calculation
- `spend` - **Calculated:** (Impressions / 1000) × CPM
- `ctr` - **Calculated:** (Clicks / Impressions) × 100
- `cpc` - **Calculated:** Spend / Clicks
- `cpa` - **Calculated:** Spend / Conversions
- `roas` - **Calculated:** Revenue / Spend

## Calculation Formulas

All formulas match the production ETL pipeline:

### Spend
```
Spend = (Impressions / 1,000) × CPM
```

### CTR (Click-Through Rate)
```
CTR = (Clicks / Impressions) × 100
```

### CPC (Cost Per Click)
```
CPC = Spend / Clicks
```

### CPA (Cost Per Acquisition)
```
CPA = Spend / Conversions
```

### ROAS (Return on Ad Spend)
```
ROAS = Revenue / Spend
```

## Example Usage

### Test with Surfside data at $17 CPM
```python
CSV_FILE = r"c:\data\surfside.csv"
SOURCE = "surfside"
CPM = 17.00
```

### Test with Vibe data at $25 CPM
```python
CSV_FILE = r"c:\data\vibe.csv"
SOURCE = "vibe"
CPM = 25.00
```

### Test with different CPM rates
```python
# Test scenario 1: Low CPM
CPM = 10.00

# Test scenario 2: High CPM
CPM = 30.00

# Test scenario 3: Client-specific CPM
CPM = 18.50
```

## Example Output

```
================================================================================
METRICS CALCULATOR TEST SCRIPT
================================================================================

================================================================================
Reading CSV: c:\data\surfside.csv
Source: surfside
CPM: $17.0
================================================================================

Original columns: ['Strategy Name', 'Placement Name', 'Creative Name', ...]
Mapped columns: ['strategy_name', 'placement_name', 'creative_name', ...]
Total rows: 496

Calculating metrics...
[OK] Calculated metrics for 496 rows

================================================================================
SUMMARY STATISTICS
================================================================================

Source:              surfside
CPM:                 $17.0
Total Rows:          496

Raw Metrics:
  Impressions:       541,210
  Clicks:            565
  Conversions:       199
  Revenue:           $24,963.38

Calculated Metrics:
  Spend:             $9,200.85
  CTR:               0.10%
  CPC:               $16.28
  CPA:               $46.24
  ROAS:              2.71x

================================================================================

[OK] Results saved to: c:\data\surfside_with_metrics.csv
[OK] Processing complete!
```

## Testing Scenarios

### 1. Validate CPM Calculation
Compare calculated `spend` with expected values:
```
Expected Spend = (Impressions / 1000) × CPM
```

### 2. Test Different CPM Rates
Run the same file with different CPMs to see impact on metrics:
- Low CPM (10): Lower spend, higher ROAS
- Medium CPM (17): Baseline
- High CPM (30): Higher spend, lower ROAS

### 3. Verify Metric Accuracy
Check calculations manually for a few rows:
- Pick a row with known values
- Calculate metrics by hand
- Compare with script output

### 4. Test Edge Cases
- Zero clicks (CPC should be 0.00)
- Zero conversions (CPA should be 0.00)
- Zero spend (ROAS should be 0.00)

## Troubleshooting

### Missing Column Error
```
ValueError: Missing required columns: ['Date', 'Campaign']
```
**Solution**: Check that your CSV has the correct column names for your source type.

### File Not Found
```
FileNotFoundError: CSV file not found
```
**Solution**: Verify the `CSV_FILE` path is correct and uses raw string `r"..."` or escaped backslashes.

### Invalid Source
```
ValueError: Invalid source: xyz
```
**Solution**: SOURCE must be one of: 'surfside', 'vibe', 'facebook'

## Notes

- All calculations use `Decimal` for precision (matches production)
- Rounding: Half-up to 2 decimal places
- Zero values handled safely (no division by zero errors)
- Column names are case-insensitive
- Empty rows are automatically removed

## Files

- `test_metrics_calculator.py` - Main script
- `TEST_METRICS_CALCULATOR_README.md` - This file
- `{filename}_with_metrics.csv` - Output file (generated)








