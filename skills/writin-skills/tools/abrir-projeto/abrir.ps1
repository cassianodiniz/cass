# Opens, in the default app, a file named by an abrirprojeto:// link (Windows).
# Link form: abrirprojeto://abrir/<Folder>/<path inside it>. <Folder> is the name of an allowed folder,
# or of a folder inside one. Allowed folders: one per line in %LOCALAPPDATA%\AbrirProjeto\pastas.txt;
# without that file, C:\Projetos.
param([string]$Url)
Add-Type -AssemblyName System.Windows.Forms
function Refuse($m) { [System.Windows.Forms.MessageBox]::Show("Recusado: $m", "Abrir arquivo do projeto") | Out-Null; exit 1 }
$cfg = Join-Path $env:LOCALAPPDATA "AbrirProjeto\pastas.txt"
$roots = @()
if (Test-Path -LiteralPath $cfg) { $roots = Get-Content -LiteralPath $cfg | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith("#") -and [System.IO.Path]::IsPathRooted($_) } }
if (-not $roots) { $roots = @("C:\Projetos") }
$roots = @($roots | ForEach-Object { [System.IO.Path]::GetFullPath($_).TrimEnd("\") })
$blocked = @(".exe",".bat",".cmd",".com",".ps1",".psm1",".vbs",".vbe",".js",".jse",".wsf",".wsh",".msi",".msp",".scr",".lnk",".url",".hta",".cpl",".reg",".py",".rb",".pl",".sh",".jar",".appref-ms")
try { $u = [System.Uri]$Url } catch { Refuse "link inválido" }
if ($u.Scheme -ne "abrirprojeto" -or $u.Host -ne "abrir") { Refuse "link fora do formato abrirprojeto://abrir/..." }
$parts = [System.Uri]::UnescapeDataString($u.AbsolutePath).Split("/") | Where-Object { $_ -ne "" }
if (-not $parts -or ($parts | Where-Object { $_ -eq "." -or $_ -eq ".." -or $_ -match '[:\\]' })) { Refuse "caminho inválido" }
$parts = @($parts)
$cands = @()
foreach ($r in $roots) { if ((Split-Path $r -Leaf) -ieq $parts[0]) { $rest = if ($parts.Count -gt 1) { $parts[1..($parts.Count-1)] -join "\" } else { "" }; $cands += [System.IO.Path]::GetFullPath((Join-Path $r $rest)) } }
foreach ($r in $roots) { $cands += [System.IO.Path]::GetFullPath((Join-Path $r ($parts -join "\"))) }
$full = $cands | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $full) { Refuse "arquivo não encontrado: $($parts -join '/')" }
if (-not ($roots | Where-Object { $full.StartsWith($_ + "\", [System.StringComparison]::OrdinalIgnoreCase) })) { Refuse "arquivo fora das pastas permitidas" }
$item = Get-Item -LiteralPath $full
if ($item.LinkType) { Refuse "atalho ou link; não abro por link" }
if ($blocked -contains $item.Extension.ToLower()) { Refuse "tipo de arquivo que roda programa; não abro por link" }
Start-Process -FilePath $full
