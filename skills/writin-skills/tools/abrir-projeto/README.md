# abrir-projeto

Link type `abrirprojeto://abrir/<Folder>/<path>` that opens a project file in the machine's default app. Used by the "Abrir arquivo" button of the change guide page.

- `<Folder>` is the name of an allowed folder, or of a folder inside one.
- You choose where it works: list the allowed folders, one full path per line, in `~/.config/abrir-projeto/pastas.txt` (Mac) or `%LOCALAPPDATA%\AbrirProjeto\pastas.txt` (Windows). Without that file: `~/Projetos` and `~/Skills` on the Mac, `C:\Projetos` on Windows.
- Refused: anything outside the allowed folders, `..`, missing files, and file types that run a program (scripts, apps, shortcuts).
- Optional. Without it the button does nothing; the rest of the page works the same.
- Install, once per machine, from this folder:
  - Mac: `./instalar-mac.sh` (creates `~/Applications/AbrirProjeto.app`). On the first click the browser asks to open it; allow.
  - Windows: `powershell -ExecutionPolicy Bypass -File instalar-windows.ps1` (no admin needed).
- Remove: Mac, delete `~/Applications/AbrirProjeto.app`; Windows, delete the registry key `HKCU\Software\Classes\abrirprojeto` and the folder `%LOCALAPPDATA%\AbrirProjeto`.
- Tested on the Mac on 2026-11-15, including the click from the published page. The Windows files were written but not run.
