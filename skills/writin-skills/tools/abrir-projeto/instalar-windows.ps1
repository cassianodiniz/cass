# Registers the abrirprojeto:// link type for the current Windows user (no admin needed).
$dest = Join-Path $env:LOCALAPPDATA "AbrirProjeto"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Force (Join-Path $PSScriptRoot "abrir.ps1") (Join-Path $dest "abrir.ps1")
$key = "HKCU:\Software\Classes\abrirprojeto"
New-Item -Force -Path "$key\shell\open\command" | Out-Null
Set-ItemProperty -Path $key -Name "(default)" -Value "URL:Abrir arquivo do projeto"
Set-ItemProperty -Path $key -Name "URL Protocol" -Value ""
$cmd = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$dest\abrir.ps1`" `"%1`""
Set-ItemProperty -Path "$key\shell\open\command" -Name "(default)" -Value $cmd
Write-Output "instalado: $dest"
