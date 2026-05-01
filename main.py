from extractor import OSINTExtractor
from graph_builder import OSINTGraphDatabase
from visualize import generate_tree_graph, generate_circular_graph # Import your new visuals
from rich.console import Console

console = Console()

def run_pipeline(text_data):
    # 1. AI Extraction
    extractor = OSINTExtractor()
    ai_result = extractor.extract(text_data)
    console.print(f"[green]Extracted {len(ai_result.triplets)} relationships.[/green]")

    # 2. Database Injection
    db = OSINTGraphDatabase()
    for t in ai_result.triplets:
        db.insert_triplet(t.subject.label, t.subject.value, t.relation, t.object.label, t.object.value)
    db.close()
    console.print("[cyan]Neo4j Database Updated.[/cyan]")

    # 3. Automatic Report Generation (FR-04 & FR-07)
    console.print("[yellow]Generating Investigator Reports...[/yellow]")
    generate_tree_graph(ai_result, 'Incident_Tree_Report.html')
    generate_circular_graph(ai_result, center_node_value="APT-44", filename='Target_Profile_Report.html')
    
    console.print("\n[bold green]✅ Pipeline Complete! Check your folder for HTML reports.[/bold green]")