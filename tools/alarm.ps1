# 红渊夜班 · 叫醒器
# 用法：powershell -ExecutionPolicy Bypass -File tools\alarm.ps1 -Text "GLM 卡住了" -Mode once
#   -Mode once  说两遍 + 短促蜂鸣（约 12 秒）
#   -Mode loud  说四遍 + 长蜂鸣 + 中间停顿（约 40 秒），用于二次升级
param(
  [string]$Text = "红渊夜班：GLM 停住了，需要你看一眼。",
  [ValidateSet('once','loud')][string]$Mode = 'once'
)

Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$zh = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'zh*' } | Select-Object -First 1
if ($zh) { $s.SelectVoice($zh.VoiceInfo.Name) }
$s.Rate = -1        # 略慢，听清
$s.Volume = 100

$loops = if ($Mode -eq 'loud') { 4 } else { 2 }
for ($i = 1; $i -le $loops; $i++) {
  if ($i -eq 1) {
    $s.Speak($Text)
  } else {
    $s.Speak("重复提醒第 $i 次。$Text")
  }
  # 蜂鸣：用不同音高区分等级
  $freq = if ($Mode -eq 'loud') { 880 } else { 660 }
  1..3 | ForEach-Object { [console]::Beep($freq, 180); Start-Sleep -Milliseconds 120 }
  Start-Sleep -Milliseconds 600
}

if ($Mode -eq 'loud') {
  # 最后一段持续嘟声，确保真的能把人吵醒
  1..6 | ForEach-Object { [console]::Beep(1200, 250); Start-Sleep -Milliseconds 150 }
}

$log = Join-Path $PSScriptRoot '_alarm.log'
"[{0}] mode={1} {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Mode, $Text |
  Out-File -FilePath $log -Append -Encoding utf8
