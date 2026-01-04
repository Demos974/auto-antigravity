# Script de Publication Automatise sur GitHub
# Pour Auto-Antigravity

Write-Host "=== Publication Automatise sur GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Etape 1: Verifier l'etat
Write-Host "[1/5] Verification de l'etat du repository..." -ForegroundColor Yellow

$gitStatus = git status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: git status a echoue" -ForegroundColor Red
    exit 1
}

if ($gitStatus -match "On branch master" -or $gitStatus -match "On branch main") {
    # Si deja sur main, c'est OK
    Write-Host "OK Deja sur branche main" -ForegroundColor Green
} else {
    # Renommer en main
    Write-Host "Renommage de master vers main..." -ForegroundColor Yellow
    git checkout -b main
}

# Etape 2: Ajouter le remote GitHub
Write-Host ""
Write-Host "[2/5] Ajout du remote GitHub..." -ForegroundColor Yellow

git remote remove origin
git remote add origin https://github.com/Demos974/auto-antigravity.git
Write-Host "OK Remote ajoute" -ForegroundColor Green

# Etape 3: Ajouter tous les fichiers
Write-Host ""
Write-Host "[3/5] Ajout des fichiers..." -ForegroundColor Yellow

git add .
Write-Host "OK Fichiers ajoutes" -ForegroundColor Green

# Etape 4: Commit
Write-Host ""
Write-Host "[4/5] Creation du commit..." -ForegroundColor Yellow

git commit -m "Initialisation propre: Auto-Antigravity - Framework multi-agents avec monitoring avance pour Google Antigravity IDE"
Write-Host "OK Commit cree" -ForegroundColor Green

# Etape 5: Push vers GitHub
Write-Host ""
Write-Host "[5/5] Publication sur GitHub..." -ForegroundColor Cyan

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCES ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Projet publie avec succes !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/Demos974/auto-antigravity" -ForegroundColor Cyan
    Write-Host "Extension: https://github.com/Demos974/auto-antigravity/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Documentation: https://github.com/Demos974/auto-antigravity/blob/main/README.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Prochaines etapes:" -ForegroundColor Yellow
    Write-Host "  1. Creer des releases GitHub (Tags de version)" -ForegroundColor White
    Write-Host "  2. Ajouter des captures d'ecran au README" -ForegroundColor White
    Write-Host "  3. Ameliorer la documentation si necessaire" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "=== ECHEC ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "ERREUR lors du push: code $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
    Write-Host "Actions possibles:" -ForegroundColor Yellow
    Write-Host "  1. Verifiez votre connexion internet" -ForegroundColor White
    Write-Host "  2. Verifiez que vous avez acces en ecriture a ce repository" -ForegroundColor White
    Write-Host "  3. Essayez de nouveau" -ForegroundColor White
}

Write-Host ""
Write-Host "Pressez n'importe quelle touche pour quitter..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
