import sys
import json
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def replay_session(filepath: str, speed: float = 1.0):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]File not found: {filepath}[/red]")
        return

    topic = data.get("topic", "Unknown Topic")
    console.print(Panel.fit(f"[bold blue]REPLAY: {topic}[/bold blue]"))
    
    history = data.get("history", [])
    
    for turn in history:
        speaker = turn.get("speaker")
        content = turn.get("content")
        phase = turn.get("phase", "Unknown")
        
        # Simulate delay for readability
        time.sleep(1.0 / speed)
        
        console.rule(f"Phase: {phase} | Turn: {turn.get('turn_number')}")
        
        if speaker == "Moderator":
            console.print(f"[bold red]Moderator:[/bold red] {content}")
        else:
            color = "cyan" if speaker == "AgentA" else "magenta"
            console.print(Panel(Markdown(content), title=f"[bold {color}]{speaker}[/bold {color}]"))

def main():
    parser = argparse.ArgumentParser(description="Replay a saved discussion log.")
    parser.add_argument("logfile", help="Path to the JSON log file")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (default: 1.0)")
    args = parser.parse_args()
    
    replay_session(args.logfile, args.speed)

if __name__ == "__main__":
    main()
