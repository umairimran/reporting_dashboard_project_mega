$files = @(
    "app\(auth)\login\page.tsx",
    "app\(dashboard)\dashboard\page.tsx",
    "app\(dashboard)\reports\page.tsx",
    "app\(dashboard)\admin\clients\page.tsx",
    "app\(dashboard)\admin\ingestion\page.tsx",
    "app\(dashboard)\admin\settings\page.tsx",
    "components\layout\Sidebar.tsx",
    "components\dashboard\KPICard.tsx",
    "components\dashboard\PlatformTabs.tsx",
    "components\dashboard\CampaignTable.tsx",
    "components\dashboard\DateRangePicker.tsx",
    "components\dashboard\PerformanceChart.tsx"
)

foreach ($file in $files) {
    $fullPath = "c:\Users\shame\Desktop\test\$file"
    if (Test-Path $fullPath) {
        (Get-Content $fullPath -Raw) -replace ' dark:[a-zA-Z0-9_\[\]/\-\.\\()]*', '' | Set-Content $fullPath -NoNewline
        Write-Host "Processed: $file"
    }
}
Write-Host "Done removing dark: classes from all files!"
