$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$filmRoot = Split-Path $PSScriptRoot -Parent
$filmPlan = Get-Content -LiteralPath (Join-Path $filmRoot 'speech-plan.json') -Raw | ConvertFrom-Json
$filmVoice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$filmVoice.SelectVoice('Microsoft Mark')
$filmVoice.Volume = 100
$filmFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000,[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,[System.Speech.AudioFormat.AudioChannel]::Mono)
$filmReport = @()
foreach ($phrase in $filmPlan) {
    $filmOutput = Join-Path $filmRoot ('public/audio/phrases/' + $phrase.id + '.wav')
    $filmRate = -2
    do {
        $filmVoice.Rate = $filmRate
        $filmVoice.SetOutputToWaveFile($filmOutput,$filmFormat)
        $filmVoice.Speak($phrase.spokenText)
        $filmVoice.SetOutputToNull()
        # Measure audible PCM, excluding the long silence SAPI appends.
        $filmBytes = [IO.File]::ReadAllBytes($filmOutput)
        $filmReader = New-Object IO.BinaryReader([IO.MemoryStream]::new($filmBytes))
        $filmReader.BaseStream.Position = 12
        $filmPcm = $null
        while ($filmReader.BaseStream.Position -lt $filmReader.BaseStream.Length) {
            $filmChunk = [Text.Encoding]::ASCII.GetString($filmReader.ReadBytes(4))
            $filmSize = $filmReader.ReadInt32()
            if ($filmChunk -eq 'data') { $filmPcm = $filmReader.ReadBytes($filmSize); break }
            $filmReader.BaseStream.Position += $filmSize + ($filmSize % 2)
        }
        $filmReader.Dispose()
        $filmFirst = -1; $filmLast = -1
        for ($filmIndex = 0; $filmIndex -lt $filmPcm.Length - 1; $filmIndex += 2) {
            if ([Math]::Abs([int][BitConverter]::ToInt16($filmPcm,$filmIndex)) -gt 65) {
                if ($filmFirst -lt 0) { $filmFirst = $filmIndex }
                $filmLast = $filmIndex
            }
        }
        $filmDuration = ($filmLast - $filmFirst) / 96000.0 + 0.105
        $filmRate++
    } while ($filmDuration -gt ($phrase.end - $phrase.start) -and $filmRate -le 4)
    $filmReport += [pscustomobject]@{id=$phrase.id;duration=$filmDuration;rate=$filmRate-1;start=$phrase.start;end=$phrase.end}
}
$filmVoice.Dispose()
$filmReport | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $filmRoot 'review/speech-generation.json') -Encoding utf8
Write-Output ('Generated ' + $filmReport.Count + ' narration phrases using Microsoft Mark.')
