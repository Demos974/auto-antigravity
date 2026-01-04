# Script d'installation de l'extension Auto-Antigravity
# Pour Windows PowerShell

Write-Host "Installation de l'extension Auto-Antigravity pour VS Code / Antigravity IDE" -ForegroundColor Cyan
Write-Host ""

# Vérifier Node.js est installé
Write-Host "Verification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "OK Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR Node.js n'est pas installe. Veuillez l'installer depuis https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Aller dans le répertoire de l'extension
$extensionDir = Join-Path $PSScriptRoot "vscode-extension"
if (-not (Test-Path $extensionDir)) {
    Write-Host "ERREUR Repertoire d'extension non trouve: $extensionDir" -ForegroundColor Red
    exit 1
}

Set-Location $extensionDir

# Installer les dépendances
Write-Host "Installation des dependances npm..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation des dependances" -ForegroundColor Red
    exit 1
}
Write-Host "OK Dependances installees" -ForegroundColor Green

# Compiler l'extension
Write-Host "Compilation de l'extension..." -ForegroundColor Yellow
npm run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la compilation" -ForegroundColor Red
    exit 1
}
Write-Host "OK Extension compilee avec succes" -ForegroundColor Green

# Créer le fichier .vsix
Write-Host "Creation du package .vsix..." -ForegroundColor Yellow
npm run package

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la creation du package" -ForegroundColor Red
    exit 1
}

$vsixFile = Get-ChildItem -Filter "*.vsix" | Select-Object -First 1
Write-Host "OK Package cree: $($vsixFile.Name)" -ForegroundColor Green

# Vérifier VS Code est installé
Write-Host ""
Write-Host "Verification de VS Code..." -ForegroundColor Yellow

try {
    $codeCmd = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCmd) {
        Write-Host "OK VS Code trouve: $($codeCmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "ATTENTION VS Code n'est pas trouve dans le PATH. Installation manuelle necessaire." -ForegroundColor Yellow
        Write-Host "   Vous pouvez installer l'extension via : Extensions -> Install from VSIX..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "ATTENTION Impossible de verifier VS Code" -ForegroundColor Yellow
}

# Demander l'installation
Write-Host ""
Write-Host "Extension prete a etre installee !" -ForegroundColor Green
Write-Host ""

$install = Read-Host "Voulez-vous installer l'extension maintenant ? (o/n)"

if ($install -eq "o" -or $install -eq "O") {
    if ($codeCmd) {
        Write-Host "Installation en cours..." -ForegroundColor Yellow
        & code --install-extension $vsixFile.FullName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "OK Extension installee avec succes !" -ForegroundColor Green
            Write-Host "   Redemarrez VS Code pour activer l'extension." -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Documentation: vscode-extension/README.md" -ForegroundColor Cyan
        } else {
            Write-Host "ERREUR lors de l'installation" -ForegroundColor Red
        }
    } else {
        Write-Host "ATTENTION VS Code n'est pas dans le PATH. Installation manuelle :" -ForegroundColor Yellow
        Write-Host "   1. Ouvrez VS Code" -ForegroundColor Cyan
        Write-Host "   2. Appuyez sur Ctrl+Shift+X pour ouvrir Extensions" -ForegroundColor Cyan
        Write-Host "   3. Cliquez sur ... -> Install from VSIX..." -ForegroundColor Cyan
        Write-Host "   4. Selectionnez: $($vsixFile.FullName)" -ForegroundColor Cyan
    }
} else {
    Write-Host "Package disponible: $($vsixFile.FullName)" -ForegroundColor Cyan
    Write-Host "   Installez-le manuellement via: Extensions -> Install from VSIX..." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Installation terminee !" -ForegroundColor Green
