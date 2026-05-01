from extractor import OSINTExtractor
from graph_builder import OSINTGraphDatabase
from rich.console import Console

console = Console()

def run_pipeline(text_data):
    console.print("\n[bold cyan]1. Starting AI Extraction...[/bold cyan]")
    
    # Initialize the AI Brain
    extractor = OSINTExtractor()
    
    # Extract the data
    ai_result = extractor.extract(text_data)
        
    console.print(f"[green]Successfully extracted {len(ai_result.triplets)} relationships![/green]")

    console.print("\n[bold cyan]2. Connecting to Neo4j Database...[/bold cyan]")
    
    # Initialize the Database Connection
    db = OSINTGraphDatabase()

    console.print("\n[bold cyan]3. Injecting Data into Graph...[/bold cyan]")
    
    # Loop through the AI's answers and push them to Neo4j
    for t in ai_result.triplets:
        db.insert_triplet(
            subject_label=t.subject.label,
            subject_value=t.subject.value,
            relation=t.relation,
            object_label=t.object.label,
            object_value=t.object.value
        )
        console.print(f"[dim]Injected: {t.subject.value} -> {t.relation} -> {t.object.value}[/dim]")

    db.close()
    console.print("\n[bold green]✅ Pipeline Complete! Check Neo4j Desktop.[/bold green]")

if __name__ == "__main__":
    # The new, complex APT-44 Threat Report
    new_threat_report = """
    I first came across the endpoint via typical subdomain enumeration. On the surface, it looked like an extremely promising target.
    Fortunately, the error messages helped me craft a properly-formatted XML file that was accepted by the server. It appeared that the external entity injection was successful.
    More than a month later, I revisited the target. Fortunately, it was still online. This time, I suspected that if the XML input was vulnerable, perhaps other inputs were too.
    However, it appeared that the apostrophe ' was being properly escaped. After a bit of testing, I realized my mistake: the XML parser and the SQL database were handling characters differently.
    With a bit more manual testing, I realized it was possible to craft a time-based SQL injection. I then switched to sqlmap with a high risk and level to see if it could automate the extraction.
    So I had an SQL injection - but what if the database was unused or negligible? I decided to test for three things: the type of database, the current user, and the current database name.
    Fortunately, Microsoft provides documentation online about Dynamics AX. After a bit of research, I found the default main tables and columns that store sensitive user information.
    As described in the Hacker Summary, @spaceraccoon discovered a SQL Injection vulnerability in a web service backed by Microsoft Dynamics AX. By exploiting this vulnerability, it was possible to read data from the database.
    """
    
    run_pipeline(new_threat_report)