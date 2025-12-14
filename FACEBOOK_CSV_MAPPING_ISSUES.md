# Facebook CSV Data Mapping Issues

**Date:** December 14, 2025

---

## Overview

The Facebook CSV contains **monthly aggregated data with date ranges** (Dec 1-13, 2025), but the dashboard requires **daily granular data**. Additionally, several mapping challenges need to be resolved.

---

## Critical Issues & Questions

### **1. Date Format**

**Issue:** CSV has date ranges (`Reporting starts: 2025-12-01` to `Reporting ends: 2025-12-13`), but database needs a single date per record.

**Question:** 
- Can you provide **daily exports** instead of monthly aggregates? (Strongly preferred)
- If not, should we use the start date or end date for each record?

---

### **2. Regional Data**

**Issue:** Same campaign/ad appears multiple times with different regions (Connecticut, New Jersey, New York).

**Example:**
- Brooklyn Bowl 1: 412 impressions (CT) + 1,376 (NJ) + 11,074 (NY)

**Question:** Should we:
- **Aggregate** all regions into one total? (Recommended)
- **Keep separate** by adding region to database? (Requires schema changes)

---

### **3. Click Metrics**

**Issue:** CSV has two click columns: `Link clicks` and `Clicks (all)`.

**Question:** Which should we use for dashboard reporting?

---

### **4. Missing Conversion Data**

**Issue:** CSV doesn't contain conversions or revenue fields.

**Impact:** Without this data:
- CPA (Cost Per Acquisition) = $0
- ROAS (Return on Ad Spend) = N/A
- Revenue metrics won't display

**Question:** Will Facebook conversion tracking be enabled for future exports?

---

### **5. Spend Calculation**

**Issue:** Facebook reports actual spend ($1,311.14), but system recalculates using your custom CPM rate.

**Example:**
- Facebook actual: $1,311.14 (CPM $14.15)
- Your CPM ($15): $1,389.80
- **Difference: $78.66**

**Question:** Is this recalculation intentional? Will the discrepancy cause confusion?

---

### **6. Campaign Hierarchy**

**Current Mapping:**
```
Campaign name → Campaign
Ad set name   → Strategy  
Ad name       → Placement & Creative (same value for both)
```

**Question:** Is it correct that Placement and Creative are identical (both = Ad name)?

---

## Quick Reference: Data Mapping

| Database Field | CSV Column | Status |
|---------------|------------|---------|
| Date | `Reporting starts` | ⚠️ Need daily data |
| Campaign | `Campaign name` | ✅ |
| Strategy | NOT IN CSV | ✅ |
| Placement | NOT IN CSV | ✅ |
| Creative | NOT IN CSV | ✅ |
| Impressions | `Impressions` | ✅ |
| Clicks | `Link clicks` OR `Clicks (all)` | ⚠️ Which one? |
| Conversions | NOT IN CSV | ❌ Defaults to 0 |
| Revenue | NOT IN CSV | ❌ Defaults to 0 |

---

