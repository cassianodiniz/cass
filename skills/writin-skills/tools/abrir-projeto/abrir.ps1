# Opens, in the default app, a file named by an abrirprojeto:// link (Windows).
# Link form: abrirprojeto://abrir/<Folder>/<path inside it>, resolved under C:\Projetos.
param([string]$Url)
Add-Type -AssemblyName System.Windows.Forms
function Refuse($m) { [System.Windows.Forms.MessageBox]::Show("Recusado: $m", "Abrir arquivo do projeto") | Out-Null; exit 1 }
$root = [System.IO.Path]::GetFullPath("C:\Projetos")
$blocked = @(".exe",".bat",".cmd",".com",".ps1",".psm1",".vbs",".vbe",".js",".jse",".wsf",".wsh",".msi",".msp",".scr",".lnk",".url",".hta",".cpl",".reg",".py",".rb",".pl",".sh",".jar",".appref-ms")
try { $u = [System.Uri]$Url } catch { Refuse "link inválido" }
if ($u.Scheme -ne "abrirprojeto" -or $u.Host -ne "abrir") { Refuse "link fora do formato abrirprojeto://abrir/..." }
$parts = [System.Uri]::UnescapeDataString($u.AbsolutePath).Split("/") | Where-Object { $_ -ne "" }
if (-not $parts -or ($parts | Where-Object { $_ -eq "." -or $_ -eq ".." -or $_ -match '[:\\]' })) { Refuse "caminho inválido" }
$full = [System.IO.Path]::GetFullPath((Join-Path $root ($parts -join "\")))
if (-not $full.StartsWith($root + "\", [System.StringComparison]::OrdinalIgnoreCase)) { Refuse "arquivo fora da pasta Projetos" }
if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { Refuse "arquivo não encontrado: $($parts -join '/')" }
$item = Get-Item -LiteralPath $full
if ($item.LinkType) { Refuse "atalho ou link; não abro por link" }
if ($blocked -contains $item.Extension.ToLower()) { Refuse "tipo de arquivo que roda programa; não abro por link" }
Start-Process -FilePath $full
