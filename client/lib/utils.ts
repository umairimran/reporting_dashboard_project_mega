import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";


export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Helper to format currency
export function formatCurrency(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

// Helper to format large numbers
export function formatNumber(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return "-";
  if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + "M";
  }
  if (value >= 1000) {
    return (value / 1000).toFixed(1) + "K";
  }
  return value.toLocaleString();
}

// Helper to format percentage
export function formatPercent(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return "-";
  return value.toFixed(2) + "%";
}
