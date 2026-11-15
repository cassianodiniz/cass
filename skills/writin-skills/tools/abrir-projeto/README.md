# abrir-projeto

Link type `abrirprojeto://abrir/<Folder>/<path>` that opens a project file in the machine's default app. Used by the "Abrir arquivo" button of the change guide page.

- `<Folder>` is a folder inside `Projetos` (Mac: `~/Projetos`; Windows: `C:\Projetos`). On the Mac, `Skills` also resolves to `~/Skills`.
- Refused: anything outside those folders, `..`, missing files, and file types that run a program (scripts, apps, shortcuts).
- Install once per machine: Mac `./instalar-mac.sh` (creates `~/Applications/AbrirProjeto.app`); Windows `powershell -ExecutionPolicy Bypass -File instalar-windows.ps1`.
- Tested on the Mac on 2026-11-15, including the click from the published page. The Windows files were written but not run.
