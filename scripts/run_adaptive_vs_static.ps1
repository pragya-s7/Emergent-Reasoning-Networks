# PowerShell script to run Experiment 2: Adaptive vs Static Comparison
# Windows-compatible version

param(
    [Parameter(Mandatory=$true)]
    [string]$AnthropicKey,
    
    [Parameter(Mandatory=$false)]
    [int]$NQueries = 5,
    
    [Parameter(Mandatory=$false)]
    [int]$Cycles = 3
)

$env:TOKENIZERS_PARALLELISM = "false"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "EXPERIMENT 2: ADAPTIVE vs STATIC COMPARISON" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:"
Write-Host "  Queries: $NQueries"
Write-Host "  Cycles: $Cycles"
Write-Host "  Model: Claude 3 Haiku"
$estimatedMinutes = [math]::Ceiling(($NQueries * $Cycles * 30) / 60)
Write-Host "  Estimated runtime: ~$($NQueries * $Cycles * 2) queries (~$estimatedMinutes minutes)"
Write-Host ""
Write-Host "This experiment compares:"
Write-Host "  [BASELINE]  Static graph (no Hebbian learning)" -ForegroundColor Yellow
Write-Host "  [TREATMENT] Adaptive graph (with Hebbian learning)" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

python scripts/evaluate_adaptive_vs_static.py `
    --anthropic-key $AnthropicKey `
    --n-queries $NQueries `
    --cycles $Cycles `
    --output-dir output `
    --seed 42

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "EXPERIMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check output/ directory for results:"
Write-Host "  - static_results_*.csv"
Write-Host "  - adaptive_results_*.csv"
Write-Host "  - comparison_summary_*.json"
Write-Host "  - adaptive_kg_cycle_*.json"
Write-Host ""

