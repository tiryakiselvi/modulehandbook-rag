param(
    [string]$SourceDirectory = "outputs\final_release"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root $SourceDirectory
$sourceChunks = Join-Path $source "chunks"
$target = Join-Path $root "data\processed"

$mapping = @(
    @{ Source = "stress_all_variants_field.jsonl"; Target = "chunks_field.jsonl" },
    @{ Source = "stress_all_variants_module.jsonl"; Target = "chunks_module.jsonl" },
    @{ Source = "stress_all_variants_naive.jsonl"; Target = "chunks_naive.jsonl" },
    @{ Source = "stress_all_variants_field.jsonl"; Target = "chunks.jsonl" }
)

if (-not (Test-Path -LiteralPath $sourceChunks)) {
    throw "Release-Chunks fehlen: $sourceChunks"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null

foreach ($entry in $mapping) {
    $from = Join-Path $sourceChunks $entry.Source
    $to = Join-Path $target $entry.Target
    if (-not (Test-Path -LiteralPath $from)) {
        throw "Quelldatei fehlt: $from"
    }
    Copy-Item -LiteralPath $from -Destination $to -Force
}

Write-Host "Demo-Daten bereit: $target"
Get-ChildItem -LiteralPath $target -Filter "chunks*.jsonl" |
    Select-Object Name, Length, LastWriteTime

