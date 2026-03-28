import argparse
import asyncio
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from keyscan.engine.scanner import Scanner

console = Console()

def print_banner():
    banner = """[bold cyan]
  _                                 
 | | _____ _   _ ___  ___ __ _ _ __  
 | |/ / _ \ | | / __|/ __/ _` | '_ \ 
 |   <  __/ |_| \__ \ (_| (_| | | | |
 |_|\_\___|\__, |___/\___\__,_|_| |_|
           |___/                     
    [/bold cyan] [yellow]v0.1.0[/yellow] - API Key Validation Engine
    """
    console.print(banner)

async def main_async(args):
    if not args.key and not args.file:
        console.print("[red]Error: Must provide either -k/--key or -f/--file[/red]")
        sys.exit(1)
        
    keys = []
    if args.key:
        keys.append(args.key)
    if args.file:
        try:
            with open(args.file, 'r') as f:
                keys.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            sys.exit(1)
            
    scanner = Scanner(templates_dir=args.templates)
    
    console.print(f"[bold]Starting scan for {len(keys)} keys...[/bold]\n")
    results = await scanner.scan_keys(keys)
    
    if args.json:
        out = [r.model_dump() for r in results]
        console.print(json.dumps(out, indent=2))
        return
        
    table = Table(title="Validation Results")
    table.add_column("Key (Masked)", style="cyan")
    table.add_column("Service", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Confidence", justify="right", style="green")
    table.add_column("Message")
    
    for r in results:
        # Mask key for output: sk_live_1234...5678
        masked = r.key[:8] + "..." + r.key[-4:] if len(r.key) > 12 else r.key
        
        status_color = "green" if r.status == "valid" else "red" if r.status == "invalid" else "yellow"
        
        table.add_row(
            masked,
            r.service,
            f"[{status_color}]{r.status.upper()}[/{status_color}]",
            f"{r.confidence:.2f}",
            r.message or ""
        )
        
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="keyscan - API Key Validation Engine")
    parser.add_argument("-k", "--key", help="Single key to validate")
    parser.add_argument("-f", "--file", help="File containing list of keys")
    parser.add_argument("-t", "--templates", default="templates", help="Directory containing YAML templates")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    if not args.json:
        print_banner()
        
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user.[/yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()
