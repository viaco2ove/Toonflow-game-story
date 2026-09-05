$ErrorActionPreference = "Continue"
$root = "D:\Users\viaco\tools\Toonflow-game\Toonflow-game-story"
$cache = "$root\.cache\character\黑塔：从超忆症开始成神"
$venv = "D:\Users\viaco\tools\Toonflow-game\Toonflow-game-app\Toonflow-game\tools\avatar-matting\birefnet\venv\Scripts\python.exe"
$convert = "$root\.workbuddy\skills\convert-avatar-video-to-webp\convert.py"

# role name -> (subdir, mp4 filename)
$roleMap = @{
    "chenxi"    = @("用户", "陈曦_6s.mp4")
    "zhangwanyi"= @("张晚意", "张晚意.mp4")
    "linfan"    = @("林凡", "林凡_6s.mp4")
    "laozhou"   = @("老周", "老周.mp4")
    "suxiao"    = @("苏晓", "苏晓.mp4")
    "weishu"    = @("魏叔", "魏叔_6s.mp4")
    "chenmu"    = @("陈母", "陈母.mp4")
    "baixiaosheng" = @("百晓生", "百晓生_6s.mp4")
    "baizixuan" = @("白子轩", "白子轩_6s.mp4")
    "xiaoman"   = @("小满", "小满_6s.mp4")
    "nv"        = @("某女子", "某女子_6s.mp4")
    "nan"       = @("某男子", "某男子_6s.mp4")
}

$jobs = @()
foreach ($key in $roleMap.Keys) {
    $subdir = $roleMap[$key][0]
    $mp4file = $roleMap[$key][1]
    $mp4 = "$cache\$subdir\$mp4file"
    $outDir = "$cache\$subdir\webp"

    if (-not (Test-Path $mp4)) {
        Write-Host "[SKIP] $key : mp4 not found: $mp4"
        continue
    }
    if ((Test-Path "$outDir\foreground.webp") -and (Test-Path "$outDir\background.png")) {
        Write-Host "[DONE] $key : webp already exists"
        continue
    }
    Write-Host "[START] $key : $mp4file -> webp"
    $job = Start-Job -ScriptBlock {
        param($py, $conv, $mp4, $outDir)
        $env:PYTHONIOENCODING = "utf-8"
        $errFile = "$outDir\_convert_err.log"
        $outFile = "$outDir\_convert_out.log"
        & $py $conv --mp4 $mp4 --out-dir $outDir 2> $errFile > $outFile
        if ($LASTEXITCODE -eq 0) {
            "ok" | Out-File "$outDir\_done.txt" -Encoding utf8
            Write-Host "[OK] done"
        } else {
            "ERROR $LASTEXITCODE" | Out-File $errFile -Append -Encoding utf8
            Write-Host "[FAIL] exit=$LASTEXITCODE"
        }
    } -ArgumentList $venv, $convert, $mp4, $outDir
    $jobs += @{ job=$job; key=$key; outDir=$outDir }
}

$total = $jobs.Count
Write-Host "`n=== $total jobs running ===`n"

# Poll every 15s
$done = 0
$elapsed = 0
while ($done -lt $total) {
    Start-Sleep 15
    $elapsed += 15
    $done = ($jobs | Where-Object { $_.job.JobStateInfo.State -eq "Completed" }).Count
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $done/$total done (${elapsed}s)"
    if ($elapsed -ge 1200) { break }
}

# Collect results
Write-Host "`n=== Collecting results ==="
foreach ($j in $jobs) {
    $null = $j.job | Wait-Job -Timeout 120 | Out-Null
    $j.job | Remove-Job -Force
    if (Test-Path "$($j.outDir)\_done.txt") {
        Write-Host "[OK] $($j.key)"
    } else {
        Write-Host "[FAIL] $($j.key)"
    }
}
Write-Host "`n=== ALL DONE ==="