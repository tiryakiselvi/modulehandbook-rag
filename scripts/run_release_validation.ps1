param(
    [string]$OutputDirectory = "outputs\final_release",
    [switch]$SkipLlmPilot
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Virtuelle Umgebung fehlt: $python"
}

Set-Location $root
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:PYTHONHASHSEED = "0"

Write-Host "[1/3] Automatisierte Tests"
& $python -m pytest -q

Write-Host "[2/3] Retrieval-Evaluation"
& $python -B scripts\run_final_evaluation.py --out $OutputDirectory

if (-not $SkipLlmPilot) {
    $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 5
    if (-not ($tags.models.name -contains "llama3.2:3b")) {
        throw "Ollama-Modell llama3.2:3b ist nicht lokal verfügbar."
    }
    Write-Host "[3/3] Kontrollierter Antwortpilot"
    & $python -B scripts\run_llm_behavior_evaluation.py `
        --results $OutputDirectory `
        --model "llama3.2:3b" `
        --repeats 3 `
        --seed 42
}
else {
    Write-Host "[3/3] Antwortpilot übersprungen"
}

Write-Host "Release-Validierung abgeschlossen: $OutputDirectory"
