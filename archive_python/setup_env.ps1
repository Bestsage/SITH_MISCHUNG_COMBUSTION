
Write-Host "🚀 Setting up Rocket Dev Environment..."

# 1. Add Rust to PATH
$rustPath = "$env:USERPROFILE\.cargo\bin"
if (Test-Path $rustPath) {
    Write-Host "✅ Found Rust at $rustPath"
    $env:PATH += ";$rustPath"
}
else {
    Write-Host "❌ Rust bin not found at $rustPath. Did install complete?"
}

# 2. Check/Add MSYS2
$msysPath = "C:\msys64"
if (Test-Path $msysPath) {
    Write-Host "✅ Found MSYS2 at $msysPath"
    $mingwPath = "$msysPath\mingw64\bin"
    
    if (Test-Path $mingwPath) {
        $env:PATH += ";$mingwPath"
        Write-Host "   Added MinGW64 to PATH"
    }
    
    # Check for GFortran
    if (Get-Command gfortran -ErrorAction SilentlyContinue) {
        Write-Host "✅ GFortran is available!"
    }
    else {
        Write-Host "⚠️ GFortran missing. Try installing it via:"
        Write-Host "   pacman -S mingw-w64-x86_64-gcc-fortran"
        Write-Host "   (Run this inside the MSYS2 Mingw64 terminal)"
    }
}
else {
    Write-Host "❌ MSYS2 not found at default location."
}

Write-Host "Environment updated for this session."
Write-Host "Try running: cargo --version"
