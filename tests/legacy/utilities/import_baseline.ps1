param(
    [Parameter(Mandatory=$true)][string]$BaselinePath,
    [string]$Tag = 'v1.0.0',
    [string]$Message = 'Pre-Phase1 baseline'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $BaselinePath)) {
    throw "BaselinePath not found: $BaselinePath"
}

Write-Host "Creating orphan branch 'baseline-import'..."
& git checkout --orphan baseline-import | Out-Null

Write-Host "Cleaning index and working tree (no files tracked)..."
& git rm -r --cached . 2>$null | Out-Null

# Remove all files in working tree except .git directory
Get-ChildItem -Force | Where-Object { $_.Name -ne '.git' } | ForEach-Object {
    if ($_.PSIsContainer) { Remove-Item -Recurse -Force $_.FullName }
    else { Remove-Item -Force $_.FullName }
}

Write-Host "Copying baseline content..."
Copy-Item -Path (Join-Path $BaselinePath '*') -Destination . -Recurse -Force

Write-Host "Staging and committing baseline..."
& git add .
& git commit -m "chore(repo): import pre-Phase1 baseline"

Write-Host "Tagging $Tag ..."
& git tag -a $Tag -m $Message

Write-Host "Switching back to 'main'..."
& git checkout main | Out-Null

Write-Host "Done. Verify tags via 'git tag -n' and history via 'git log --graph --decorate --oneline --all'"