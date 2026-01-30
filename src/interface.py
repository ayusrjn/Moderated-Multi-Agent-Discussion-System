from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from .controller import DiscussionController
from .models import DiscussionPhase

console = Console()

class ModeratorInterface:
    def __init__(self, controller: DiscussionController):
        self.controller = controller

    def display_welcome(self):
        console.print(Panel.fit("[bold blue]Triadic LLM Discussion System[/bold blue]\n[italic]Two Agents + Human Moderator[/italic]"))

    def run_loop(self):
        self.display_welcome()
        
        # Initial Setup
        topic = Prompt.ask("Enter discussion topic")
        self.controller.start_discussion(topic)
        console.print(f"[green]Discussion started on: {topic}[/green]")
        
        while True:
            # Display Status
            state = self.controller.state
            status_text = f"Turn: {state.turn_number} | Phase: {state.discussion_phase.value} | Next: {self.controller.next_speaker()} | Paused: {list(self.controller.paused_agents)}"
            console.rule(status_text)

            # Get Command
            cmd = Prompt.ask("[bold red]Moderator Command[/bold red]", default="NEXT")
            
            self._handle_command(cmd)

    def _handle_command(self, cmd: str):
        parts = cmd.strip().split(" ", 1)
        action = parts[0].upper()
        payload = parts[1] if len(parts) > 1 else ""

        if action == "NEXT":
            speaker = self.controller.next_speaker()
            console.print(f"[yellow]Executing turn for {speaker}...[/yellow]")
            response = self.controller.execute_agent_turn(speaker)
            
            color = "cyan" if speaker == "AgentA" else "magenta"
            console.print(Panel(Markdown(response), title=f"[bold {color}]{speaker}[/bold {color}]"))
            
        elif action == "INTERJECT":
            console.print(f"[bold red]Moderator:[/bold red] {payload}")
            self.controller.moderator_interject(payload)
            
        elif action == "PHASE":
            try:
                new_phase = DiscussionPhase(payload.capitalize())
                self.controller.set_phase(new_phase)
                console.print(f"[green]Phase changed to {new_phase.value}[/green]")
            except ValueError:
                console.print("[red]Invalid Phase. Options: Introduction, Argumentation, Synthesis, Conclusion[/red]")

        elif action == "PAUSE":
            msg = self.controller.pause_agent(payload)
            console.print(f"[yellow]{msg}[/yellow]")

        elif action == "UNPAUSE":
            msg = self.controller.unpause_agent(payload)
            console.print(f"[yellow]{msg}[/yellow]")
            
        elif action == "REPHRASE":
            msg = self.controller.request_rephrase()
            console.print(f"[bold red]{msg}[/bold red]")

        elif action == "EVIDENCE":
             # Usage: EVIDENCE AgentA
             msg = self.controller.demand_evidence(payload)
             console.print(f"[bold red]{msg}[/bold red]")

        elif action == "QUIT" or action == "EXIT":
            console.print("[dim]Saving session log...[/dim]")
            try:
                log_file = self.controller.save_session()
                console.print(f"[green]Session saved to {log_file}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to save session: {e}[/red]")
            
            console.print("[bold]Terminating session.[/bold]")
            exit(0)
            
        else:
            console.print("[dim]Unknown command.[/dim]")
