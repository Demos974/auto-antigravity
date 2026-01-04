"""
Exemple d'utilisation d'Auto-Antigravity
"""
import asyncio
from auto_antigravity import AutoAntigravity


async def main():
    """Exemple d'utilisation"""
    # Initialiser Auto-Antigravity
    aa = AutoAntigravity()
    
    # Initialiser avec vos clés API
    await aa.initialize(
        gemini_api_key="votre_cle_gemini_ici",
        anthropic_api_key="votre_cle_anthropic_ici",
        openai_api_key="votre_cle_openai_ici"
    )
    
    # Exécuter une tâche
    result = await aa.execute_task(
        task_description="Créer une application web simple avec Flask qui affiche 'Hello World'",
        project_path="./my_flask_app",
        project_name="MyFlaskApp",
        project_description="Une application Flask simple"
    )
    
    # Afficher le résultat
    if result["success"]:
        print("✓ Tâche accomplie avec succès!")
        print(f"Tâches complétées: {result['context']['tasks_completed']}")
        print(f"Fichiers créés: {result['context']['files_created']}")
    else:
        print(f"✗ Erreur: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())
