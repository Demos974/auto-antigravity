"""
Point d'entrée principal pour Auto-Antigravity
"""
import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import AutoAntigravity
from .utils.logger import setup_logger, get_logger

app = typer.Typer()
console = Console()


@app.command()
def run(
    task: str = typer.Option(..., "--task", "-t", help="Description de la tâche à accomplir"),
    project_path: str = typer.Option("./workspace", "--path", "-p", help="Chemin du projet"),
    project_name: str = typer.Option("MyProject", "--name", "-n", help="Nom du projet"),
    description: str = typer.Option("", "--description", "-d", help="Description du projet"),
):
    """Exécute Auto-Antigravity avec la tâche spécifiée"""
    
    # Afficher la bannière
    console.print(Panel(
        Text("Auto-Antigravity", style="bold magenta"),
        subtitle="Framework Multi-Agents pour l'IDE Antigravity",
        border_style="magenta"
    ))
    console.print()
    
    # Logger setup
    setup_logger()
    logger = get_logger()
    
    # Récupérer les clés API depuis l'environnement
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not gemini_api_key:
        console.print("[red]Erreur: GEMINI_API_KEY non définie[/red]")
        console.print("Définissez-la dans le fichier .env ou via les variables d'environnement")
        raise typer.Exit(1)
    
    if not anthropic_api_key:
        console.print("[red]Erreur: ANTHROPIC_API_KEY non définie[/red]")
        console.print("Définissez-la dans le fichier .env ou via les variables d'environnement")
        raise typer.Exit(1)
    
    if not openai_api_key:
        console.print("[red]Erreur: OPENAI_API_KEY non définie[/red]")
        console.print("Définissez-la dans le fichier .env ou via les variables d'environnement")
        raise typer.Exit(1)
    
    # Exécuter la tâche
    try:
        result = asyncio.run(run_auto_antigravity(
            task_description=task,
            project_path=project_path,
            project_name=project_name,
            project_description=description,
            gemini_api_key=gemini_api_key,
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key
        ))
        
        # Afficher le résultat
        if result.get("success"):
            console.print(Panel(
                f"[green]✓ Tâche accomplie avec succès![/green]\n\n"
                f"Tâches complétées: {result['context']['tasks_completed']}\n"
                f"Fichiers créés: {len(result['context']['files_created'])}\n"
                f"Itérations: {result['context']['total_iterations']}",
                title="Résultat",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]✗ Erreur lors de l'exécution[/red]\n\n"
                f"{result.get('error', 'Erreur inconnue')}",
                title="Erreur",
                border_style="red"
            ))
    
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")
        raise typer.Exit(1)


async def run_auto_antigravity(
    task_description: str,
    project_path: str,
    project_name: str,
    project_description: str,
    gemini_api_key: str,
    anthropic_api_key: str,
    openai_api_key: str
) -> dict:
    """Exécute Auto-Antigravity"""
    logger = get_logger()
    
    aa = AutoAntigravity()
    
    await aa.initialize(gemini_api_key, anthropic_api_key, openai_api_key)
    
    return await aa.execute_task(
        task_description=task_description,
        project_path=project_path,
        project_name=project_name,
        project_description=project_description
    )


@app.command()
def init():
    """Initialise le fichier de configuration .env"""
    from pathlib import Path
    
    env_file = Path(".env")
    
    if env_file.exists():
        console.print("[yellow]Le fichier .env existe déjà[/yellow]")
        overwrite = typer.confirm("Voulez-vous le remplacer?")
        if not overwrite:
            console.print("Annulé.")
            raise typer.Exit()
    
    env_content = """# Configuration Auto-Antigravity

# Clés API (obligatoires)
GEMINI_API_KEY=votre_cle_gemini_ici
ANTHROPIC_API_KEY=votre_cle_anthropic_ici
OPENAI_API_KEY=votre_cle_openai_ici

# API Antigravity (optionnel)
ANTIGRAVITY_API_URL=http://localhost:8080
ANTIGRAVITY_API_KEY=votre_cle_antigravity_ici

# Modèles par défaut
DEFAULT_MODEL=gemini-3-pro
CODER_MODEL=claude-sonnet-4.5
TESTER_MODEL=gpt-oss

# Configuration des Agents
MAX_RETRIES=3
TIMEOUT=300
MAX_ITERATIONS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/auto_antigravity.log

# Chemins
WORKSPACE=./workspace
BACKUP_DIR=./backups
TEMP_DIR=./temp

# Sécurité
ENABLE_SANDBOX=true
ENABLE_BACKUP=true
MAX_FILE_SIZE=10485760
"""
    
    env_file.write_text(env_content)
    
    console.print(Panel(
        f"[green]✓ Fichier .env créé[/green]\n\n"
        "[cyan]Éditez-le maintenant et ajoutez vos clés API:[/cyan]\n"
        "  - GEMINI_API_KEY\n"
        "  - ANTHROPIC_API_KEY\n"
        "  - OPENAI_API_KEY",
        title="Initialisation",
        border_style="green"
    ))


@app.command()
def version():
    """Affiche la version d'Auto-Antigravity"""
    from . import __version__
    console.print(f"Auto-Antigravity version {__version__}")


if __name__ == "__main__":
    app()
