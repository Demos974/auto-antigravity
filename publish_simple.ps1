# Script de Publication sur GitHub
# Version simple et robuste

Write-Host "=== PUBLICATION SUR GITHUB ===" -ForegroundColor Cyan
Write-Host ""

# Ajouter le remote
git remote add origin https://github.com/Demos974/auto-antigravity.git

# Pousser le code
git push -u origin main

Write-Host ""
Write-Host "=== FIN ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Votre code est sur GitHub:" -ForegroundColor Green
Write-Host "https://github.com/Demos974/auto-antigravity" -ForegroundColor Cyan
Write-Host ""
Write-Host "Extension VS Code:" -ForegroundColor Yellow
Write-Host "https://github.com/Demos974/auto-antigravity/releases" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour des mises a jour, utilisez:" -ForegroundColor Gray
Write-Host "git add ." -ForegroundColor White
Write-Host "git commit -m 'Description'" -ForegroundColor White
Write-Host "git push" -ForegroundColor White
