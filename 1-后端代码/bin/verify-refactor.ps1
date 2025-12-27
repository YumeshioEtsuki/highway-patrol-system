# Refactor Verification Script
# Check all files are correctly in place

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tasks Center Refactor - File Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "d:\MySQL Project\highway-patrol-system\1-后端代码"
$allPass = $true

function Test-FileExists {
    param(
        [string]$Path,
        [string]$Description
    )
    
    $fullPath = Join-Path $baseDir $Path
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "✓ $Description" -ForegroundColor Green
        Write-Host "  路径: $Path" -ForegroundColor Gray
        Write-Host "  大小: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Gray
        Write-Host ""
        return $true
    } else {
        Write-Host "✗ $Description" -ForegroundColor Red
        Write-Host "  路径: $Path (文件不存在)" -ForegroundColor Red
        Write-Host ""
        $script:allPass = $false
        return $false
    }
}

Write-Host "[Step 1] Check Core Files" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
Test-FileExists "templates\tasks.html" "Tasks HTML (Refactored)"
Test-FileExists "templates\tasks.html.backup" "Original Backup"
Test-FileExists "static\js\tasks.js" "Tasks JavaScript"
Test-FileExists "static\js\common.js" "Common Utils"

Write-Host "[Step 2] Check Documentation" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
Test-FileExists "docs\INTEGRATION_GUIDE.md" "Integration Guide"
Test-FileExists "docs\DESIGN_ADVANTAGES.md" "Design Advantages"
Test-FileExists "docs\PATROL_REFACTOR_EXAMPLE.md" "Patrol Refactor Example"
Test-FileExists "ANALYSIS_AND_REFACTOR_REPORT.md" "Analysis Report"
Test-FileExists "SECURITY_AND_EVOLUTION.md" "Security Guide"
Test-FileExists "README_REFACTOR.md" "Quick Summary"

Write-Host "[Step 3] Check File Content" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

# Check tasks.html contains refactored markers
$tasksHtml = Get-Content (Join-Path $baseDir "templates\tasks.html") -Raw -Encoding UTF8
if ($tasksHtml -match "taREDACTEDcategory|formContainer|taskCategories") {
    Write-Host "[OK] tasks.html contains refactored markers" -ForegroundColor Green
} else {
    Write-Host "[FAIL] tasks.html may not be replaced correctly" -ForegroundColor Red
    $allPass = $false
}

# Check tasks.js contains TASK_CONFIG
$tasksJs = Get-Content (Join-Path $baseDir "static\js\tasks.js") -Raw -Encoding UTF8
if ($tasksJs -match "TASK_CONFIG") {
    Write-Host "[OK] tasks.js contains TASK_CONFIG" -ForegroundColor Green
} else {
    Write-Host "[FAIL] tasks.js content abnormal" -ForegroundColor Red
    $allPass = $false
}

# Check common.js contains utility functions
$commonJs = Get-Content (Join-Path $baseDir "static\js\common.js") -Raw -Encoding UTF8
if ($commonJs -match "showNotification") {
    Write-Host "[OK] common.js contains utility functions" -ForegroundColor Green
} else {
    Write-Host "[FAIL] common.js content abnormal" -ForegroundColor Red
    $allPass = $false
}

Write-Host ""
Write-Host "[Step 4] Check HTML References" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

if ($tasksHtml -match "common\.js") {
    Write-Host "[OK] tasks.html references common.js" -ForegroundColor Green
} else {
    Write-Host "[FAIL] tasks.html does not reference common.js" -ForegroundColor Red
    $allPass = $false
}

if ($tasksHtml -match "tasks\.js") {
    Write-Host "[OK] tasks.html references tasks.js" -ForegroundColor Green
} else {
    Write-Host "[FAIL] tasks.html does not reference tasks.js" -ForegroundColor Red
    $allPass = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allPass) {
    Write-Host "[SUCCESS] All checks passed! Refactor deployed correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Start app: python app.py" -ForegroundColor White
    Write-Host "2. Visit: http://localhost:8000/tasks" -ForegroundColor White
    Write-Host "3. Read docs: docs\INTEGRATION_GUIDE.md" -ForegroundColor White
} else {
    Write-Host "[FAILED] Some checks failed. Please review errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix Suggestions:" -ForegroundColor Yellow
    Write-Host "1. Confirm files are replaced/copied correctly" -ForegroundColor White
    Write-Host "2. Check file paths" -ForegroundColor White
    Write-Host "3. Re-run file operations" -ForegroundColor White
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Statistics
Write-Host "[Statistics]" -ForegroundColor Cyan
$htmlSize = (Get-Item (Join-Path $baseDir "templates\tasks.html")).Length
$jsSize = (Get-Item (Join-Path $baseDir "static\js\tasks.js")).Length
$commonSize = (Get-Item (Join-Path $baseDir "static\js\common.js")).Length
$backupSize = (Get-Item (Join-Path $baseDir "templates\tasks.html.backup")).Length

Write-Host "Original HTML: $([math]::Round($backupSize/1KB, 2)) KB (~1067 lines)" -ForegroundColor Gray
Write-Host "Refactored HTML: $([math]::Round($htmlSize/1KB, 2)) KB (~615 lines)" -ForegroundColor Gray
Write-Host "Reduced: $([math]::Round(($backupSize - $htmlSize) / $backupSize * 100, 1))%" -ForegroundColor Green
Write-Host ""
Write-Host "tasks.js: $([math]::Round($jsSize/1KB, 2)) KB" -ForegroundColor Gray
Write-Host "common.js: $([math]::Round($commonSize/1KB, 2)) KB" -ForegroundColor Gray
Write-Host ""
