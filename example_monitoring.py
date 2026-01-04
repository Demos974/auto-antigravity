"""
Exemple d'utilisation du système de monitoring pour Auto-Antigravity
Cet exemple montre comment utiliser les fonctionnalités de monitoring inspirées
de l'extension Antigravity Panel
"""
import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json

# Note: Assurez-vous d'avoir installé les dépendances
# pip install -r requirements.txt

async def main():
    """Exemple d'utilisation du système de monitoring"""
    
    console = Console()
    
    # Afficher la bannière
    console.print(Panel(
        Text("Monitoring Dashboard", style="bold magenta"),
        subtitle="Système de monitoring pour Auto-Antigravity",
        border_style="magenta"
    ))
    console.print()
    
    # Importer AutoAntigravity
    try:
        from auto_antigravity import AutoAntigravity
    except ImportError:
        console.print("[red]Erreur: auto_antigravity n'est pas installé[/red]")
        console.print("Installez le projet avec: pip install -e .")
        return
    
    # Initialiser AutoAntigravity
    aa = AutoAntigravity()
    
    # Initialiser avec vos clés API
    try:
        await aa.initialize(
            gemini_api_key="votre_clé_gemini_ici",
            anthropic_api_key="votre_clé_anthropic_ici",
            openai_api_key="votre_clé_openai_ici"
        )
    except Exception as e:
        console.print(f"[red]Erreur lors de l'initialisation: {e}[/red]")
        console.print("Vérifiez vos clés API dans le fichier .env")
        return
    
    # Récupérer l'orchestrateur
    orchestrator = aa.orchestrator
    
    if not orchestrator.enable_monitoring:
        console.print("[yellow]Le monitoring est désactivé. Réactivez-le en passant enable_monitoring=True[/yellow]")
        return
    
    console.print("[green]✓ Système de monitoring activé[/green]")
    console.print()
    
    # 1. Afficher le résumé des agents
    console.print(Panel("[bold cyan]1. Résumé des Agents[/bold cyan]", border_style="cyan"))
    
    agents_summary = orchestrator.get_agents_summary()
    
    if "error" not in agents_summary:
        # Créer un tableau pour les agents
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Statut", style="yellow")
        table.add_column("Tâches", style="blue")
        table.add_column("Succès", style="green")
        
        for agent in agents_summary.get("agents", []):
            status_style = "green" if agent["status"] == "idle" else "yellow"
            table.add_row(
                agent["name"],
                agent["type"],
                f"[{status_style}]{agent['status']}[/{status_style}]",
                str(agent["total_tasks"]),
                f"{agent['success_rate']:.1f}%"
            )
        
        console.print(table)
        console.print(f"Total: {agents_summary['total_agents']} agents | "
                    f"Actifs: {agents_summary['active_agents']} | "
                    f"Erreurs: {agents_summary['error_agents']}")
    console.print()
    
    # 2. Afficher le résumé des quotas
    console.print(Panel("[bold cyan]2. Résumé des Quotas[/bold cyan]", border_style="cyan"))
    
    quota_summary = orchestrator.get_quota_summary()
    
    if "error" not in quota_summary:
        for model in quota_summary.get("models", []):
            # Afficher les quotas par modèle
            thinking_color = "green"
            if model["thinking_percentage"] < 30:
                thinking_color = "yellow"
            if model["thinking_percentage"] < 10:
                thinking_color = "red"
            
            flow_color = "green"
            if model["flow_percentage"] < 30:
                flow_color = "yellow"
            if model["flow_percentage"] < 10:
                flow_color = "red"
            
            console.print(f"  Model: [cyan]{model['name']}[/cyan]")
            console.print(f"    Thinking: [{thinking_color}]{model['thinking_percentage']:.1f}%[/{thinking_color}] "
                        f"({model['thinking_used']}/{model['thinking_limit']})")
            console.print(f"    Flow: [{flow_color}]{model['flow_percentage']:.1f}%[/{flow_color}] "
                        f"({model['flow_used']}/{model['flow_limit']})")
            console.print()
        
        if quota_summary.get("warnings"):
            console.print(f"[yellow]⚠ Avertissements: {', '.join(quota_summary['warnings'])}[/yellow]")
        if quota_summary.get("critical"):
            console.print(f"[red]🔴 Critique: {', '.join(quota_summary['critical'])}[/red]")
    console.print()
    
    # 3. Afficher le résumé du cache
    console.print(Panel("[bold cyan]3. Résumé du Cache[/bold cyan]", border_style="cyan"))
    
    cache_summary = orchestrator.get_cache_summary()
    
    if "error" not in cache_summary:
        console.print(f"  Entrées totales: [cyan]{cache_summary['total_entries']}[/cyan]")
        console.print(f"  Taille totale: [cyan]{cache_summary['total_size_mb']:.2f} MB[/cyan]")
        console.print(f"  Fichiers totaux: [cyan]{cache_summary['total_files']}[/cyan]")
        console.print()
        
        if cache_summary.get("by_agent_type"):
            console.print("  Par type d'agent:")
            for agent_type, data in cache_summary["by_agent_type"].items():
                console.print(f"    [green]{agent_type}[/green]: {data['count']} entrées, {data['size_mb']:.2f} MB")
    console.print()
    
    # 4. Afficher les tendances d'utilisation
    console.print(Panel("[bold cyan]4. Tendances d'Utilisation[/bold cyan]", border_style="cyan"))
    
    trends = orchestrator.get_usage_trends(minutes=90)
    
    if "error" not in trends:
        for trend in trends.get("trends", []):
            console.print(f"  Modèle: [cyan]{trend['family']}[/cyan]")
            console.print(f"    Points de données: {len(trend['thinking_credits'])}")
            if trend['thinking_credits']:
                avg_thinking = sum(trend['thinking_credits']) / len(trend['thinking_credits'])
                avg_flow = sum(trend['flow_credits']) / len(trend['flow_credits'])
                console.print(f"    Moyenne Thinking: {avg_thinking:.1f}")
                console.print(f"    Moyenne Flow: {avg_flow:.1f}")
    console.print()
    
    # 5. Afficher les statistiques Auto-Accept
    console.print(Panel("[bold cyan]5. Statistiques Auto-Accept[/bold cyan]", border_style="cyan"))
    
    auto_accept_stats = orchestrator.get_auto_accept_stats()
    
    if "error" not in auto_accept_stats:
        console.print(f"  Mode: [{'green' if auto_accept_stats['enabled'] else 'red'}]{auto_accept_stats['enabled']}[/{'green' if auto_accept_stats['enabled'] else 'red'}]")
        console.print(f"  Actions traitées: [cyan]{auto_accept_stats['actions_processed']}[/cyan]")
        console.print(f"  Acceptées automatiquement: [green]{auto_accept_stats['actions_auto_accepted']}[/green]")
        console.print(f"  Rejetées: [red]{auto_accept_stats['actions_rejected']}[/red]")
        console.print(f"  Taux d'acceptation: [cyan]{auto_accept_stats['auto_accept_rate']:.1f}%[/cyan]")
        console.print()
        
        # Afficher les règles
        console.print("  Règles:")
        for rule_name, rule_info in auto_accept_stats.get("rules", {}).items():
            status = "✓" if rule_info["enabled"] else "✗"
            color = "green" if rule_info["enabled"] else "red"
            console.print(f"    [{color}]{status}[/{color}] {rule_name}")
    console.print()
    
    # 6. Exécuter un diagnostic
    console.print(Panel("[bold cyan]6. Diagnostic du Système[/bold cyan]", border_style="cyan"))
    
    diag = await orchestrator.run_diagnostics()
    
    if "error" not in diag:
        console.print(f"  Statut: [{'green' if diag['success'] else 'red'}]"
                    f"{'Sain' if diag['success'] else 'Erreurs détectées'}[/{'green' if diag['success'] else 'red'}]")
        console.print()
        
        for component, data in diag["diagnostics"].items():
            status_color = "green" if data["status"] == "ok" else "red"
            console.print(f"  [{status_color}]●[/{status_color}] {component}: {data['status']}")
            if data.get("latency_ms"):
                console.print(f"    Latence: {data['latency_ms']} ms")
            if data.get("error"):
                console.print(f"    Erreur: [red]{data['error']}[/red]")
    console.print()
    
    # 7. Afficher les métriques système
    console.print(Panel("[bold cyan]7. Métriques Système[/bold cyan]", border_style="cyan"))
    
    metrics = await orchestrator.get_system_metrics()
    
    if metrics["success"] and metrics.get("metrics"):
        m = metrics["metrics"]
        console.print(f"  CPU: [cyan]{m['cpu']['usage_percent']:.1f}%[/cyan]")
        console.print(f"  Mémoire: [cyan]{m['memory']['usage_percent']:.1f}%[/cyan] "
                    f"({m['memory']['available_gb']:.1f} GB disponibles)")
        console.print(f"  Disque: [cyan]{m['disk']['usage_percent']:.1f}%[/cyan] "
                    f"({m['disk']['free_gb']:.1f} GB libres)")
        console.print(f"  Processus: [cyan]{m['processes']['count']}[/cyan]")
    console.print()
    
    # 8. Démonstration du nettoyage du cache
    console.print(Panel("[bold cyan]8. Nettoyage du Cache[/bold cyan]", border_style="cyan"))
    
    # Exécuter un auto-clean
    cleaned = orchestrator.auto_clean_cache()
    console.print(f"  Entrées nettoyées automatiquement: [green]{cleaned}[/green]")
    console.print()
    
    # 9. Toggle Auto-Accept
    console.print(Panel("[bold cyan]9. Toggle Auto-Accept[/bold cyan]", border_style="cyan"))
    
    current_state = orchestrator.auto_accept.enabled if orchestrator.auto_accept else False
    new_state = orchestrator.toggle_auto_accept()
    console.print(f"  Auto-Accept: [{'red' if current_state else 'green'}]{current_state}[/{'red' if current_state else 'green'}] → "
                f"[{'green' if new_state else 'red'}]{new_state}[/{'green' if new_state else 'red'}]")
    
    # Remettre à l'état original
    orchestrator.toggle_auto_accept()
    console.print()
    
    # Résumé final
    console.print(Panel(
        f"[green]✓ Monitoring complet terminé![/green]\n\n"
        f"Cet exemple montre toutes les fonctionnalités de monitoring disponibles dans Auto-Antigravity:\n"
        f"  • Dashboard des agents et quotas\n"
        f"  • Gestion du cache avec auto-clean\n"
        f"  • Mode Auto-Accept configurable\n"
        f"  • Outils de récupération et diagnostics\n"
        f"  • Métriques système en temps réel\n\n"
        f"Pour plus d'informations, consultez la documentation dans [cyan]monitoring/[/cyan]",
        title="Résumé",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(main())
