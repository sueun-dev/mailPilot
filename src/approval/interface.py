"""Approval interface for reviewing and approving email drafts."""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Dict, Optional

from utils.logging_config import get_logger

# Module logger
logger = get_logger(__name__)


class ApprovalInterface:
    """CLI interface for reviewing and approving email drafts."""
    
    def __init__(self):
        """Initialize the approval interface."""
        self.console = Console()
    
    def display_draft(self, draft: Dict) -> bool:
        """Display email draft and get approval."""
        # Header
        self.console.print("\n[bold blue]📧 Email Draft Review[/bold blue]\n")
        
        # Email details
        self.console.print(f"[bold]To:[/bold] {draft['to']}")
        self.console.print(f"[bold]Subject:[/bold] {draft['subject']}")
        self.console.print(f"[bold]Thread ID:[/bold] {draft.get('thread_id', 'New Thread')}\n")
        
        # Email body
        body_panel = Panel(
            draft['body'],
            title="[bold]Email Body[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(body_panel)
        
        # Thread context if available
        if draft.get('context'):
            self.console.print("\n[bold yellow]📜 Conversation Context:[/bold yellow]")
            context_panel = Panel(
                draft['context'],
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(context_panel)
        
        # Approval prompt
        self.console.print("\n")
        try:
            approved = Confirm.ask(
                "[bold green]Send this email?[/bold green]",
                default=False
            )
        except UnicodeDecodeError:
            # Fallback to simple input
            self.console.print("[bold green]Send this email? (y/n):[/bold green] ", end="")
            response = input().strip().lower()
            approved = response in ['y', 'yes']
        
        # Log the approval decision
        logger.info(f"Draft approval: {'approved' if approved else 'rejected'}", extra={
            "to": draft.get('to', ''),
            "thread_id": draft.get('thread_id', 'new'),
            "has_context": bool(draft.get('context'))
        })
        
        return approved
    
    def display_message(self, message: str, message_type: str = "info"):
        """Display a status message with type-based styling."""
        if message_type == "success":
            self.console.print(f"✅ {message}", style="bold green")
        elif message_type == "error":
            self.console.print(f"❌ {message}", style="bold red")
        elif message_type == "warning":
            self.console.print(f"⚠️ {message}", style="bold yellow")
        else:  # info
            self.console.print(f"ℹ️ {message}", style="bold blue")
    
    def display_thread_summary(self, summary: Dict):
        """Display thread summary information."""
        panel = Panel(
            f"Customer: {summary['customer_email']}\n"
            f"Messages: {summary['message_count']}\n"
            f"Created: {summary['created_at']}\n"
            f"Zoom Scheduled: {'✅' if summary['zoom_scheduled'] else '❌'}",
            title=f"[bold]Thread {summary['thread_id'][:8]}...[/bold]",
            border_style="magenta"
        )
        self.console.print(panel)
    
    
    def prompt_action(self) -> str:
        """Prompt for next action."""
        while True:
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1. Send marketing emails (YouTube Shorts Auto Generator)")
            self.console.print("2. Check for new emails and responses")
            self.console.print("3. View active threads")
            self.console.print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            self.console.print("[red]Invalid choice. Please enter 1, 2, 3, or 4.[/red]")