param([switch]$ConfigureOnly, [switch]$EnvironmentOnly, [string]$QtRoot = 'C:\launcher-tools\Qt\6.11.2\msvc2022_64', [string]$InstallDirectory = 'install')
$ErrorActionPreference = 'Stop'
$env:VSLANG = '1033'
$workspace = Split-Path -Parent $PSScriptRoot
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$installation = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installation) { throw 'Install Visual Studio Build Tools with the Desktop C++ workload.' }
$vcvars = Join-Path $installation 'VC\Auxiliary\Build\vcvars64.bat'
$environmentLines = & $env:ComSpec /c "call `"$vcvars`" >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Could not initialize Visual Studio build environment.' }
foreach ($line in $environmentLines) {
    if ($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
}
$env:Path = "$env:USERPROFILE\.local\bin;$QtRoot\bin;$env:Path"
$java = Get-ChildItem 'C:\Program Files\Zulu' -Directory -ErrorAction SilentlyContinue | Where-Object Name -Like '*17*' | Select-Object -First 1
if ($java) { $env:JAVA_HOME = $java.FullName; $env:Path = "$env:JAVA_HOME\bin;$env:Path" }
if ($EnvironmentOnly) { return }
Push-Location $workspace
try {
    cmake --preset default -DQt6_DIR="$QtRoot\lib\cmake\Qt6" -DENABLE_LTO=OFF -DLauncher_BUILD_PLATFORM=sharpness-local
    if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed.' }
    if (-not $ConfigureOnly) {
        cmake --build --preset default --config Release --parallel 4
        if ($LASTEXITCODE -ne 0) { throw 'Compilation failed.' }
        ctest --preset default --build-config Release
        if ($LASTEXITCODE -ne 0) { throw 'Launcher tests failed.' }
        $env:SHARPNESS_EXE = Join-Path $workspace 'build\Release\sharpnesslauncher.exe'
        if (Get-Command uv -ErrorAction SilentlyContinue) { uv run python -m unittest discover -s tests/ai -v }
        else { python -m unittest discover -s tests/ai -v }
        if ($LASTEXITCODE -ne 0) { throw 'AI integration tests failed.' }
        cmake --install build --config Release --prefix $InstallDirectory
        if ($LASTEXITCODE -ne 0) { throw 'Installation failed.' }
        & "$QtRoot\bin\windeployqt.exe" --release --no-translations (Join-Path $InstallDirectory 'sharpnesslauncher.exe')
        if ($LASTEXITCODE -ne 0) { throw 'Qt deployment failed.' }
    }
} finally { Pop-Location }
