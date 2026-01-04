"""
Script de démarrage du serveur Auto-Antigravity
"""
import sys
import os

# Ajouter le dossier parent au PYTHONPATH pour permettre les imports absolus (ex: from core.orchestrator ...)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serveur Auto-Antigravity")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=5555, help="Port d'écoute")
    
    args = parser.parse_args()
    
    # Auto-Install Dependencies
    import subprocess
    import importlib
    
    REQUIRED_PACKAGES = [
        "fastapi", "uvicorn", "psutil", "httpx", "python-dotenv", 
        "pydantic", "loguru", "pydantic-settings"
    ]
    
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        module_name = package.replace("-", "_")
        if package == "python-dotenv": module_name = "dotenv"
        
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        print(f"[AUTO-INSTALL] Installation des dépendances manquantes: {', '.join(missing_packages)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            print("[AUTO-INSTALL] Installation terminée.")
        except Exception as e:
            print(f"[ERROR] Échec de l'installation auto: {e}")

    # [AUTO-AUTH] Découverte du token (Méthode Reverse Engineering)
    try:
        if "ANTIGRAVITY_API_KEY" not in os.environ:
            import psutil
            print("[AUTH] Recherche automatique du token Antigravity...")
            for proc in psutil.process_iter(['name', 'environ']):
                try:
                    # On cherche dans les processus Antigravity ou Node
                    if proc.info['name'] and ("antigravity" in proc.info['name'].lower() or "node" in proc.info['name'].lower()):
                        env = proc.info['environ']
                        if env and "ANTHROPIC_AUTH_TOKEN" in env:
                            token = env["ANTHROPIC_AUTH_TOKEN"]
                            os.environ["ANTIGRAVITY_API_KEY"] = token
                            # On exporte aussi pour le client API si besoin
                            print(f"[AUTH] ✅ Token détecté et injecté: {token[:15]}...")
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    except Exception as e:
        print(f"[AUTH] Warning: Auto-découverte échouée ({e})")

    # Import local seulement (Maintenant que l'ENV est prêt)
    from api import run_server
    
    print(f"[AUTO-ANTIGRAVITY] Demarrage du serveur sur http://{args.host}:{args.port}")
    run_server(host=args.host, port=args.port)
