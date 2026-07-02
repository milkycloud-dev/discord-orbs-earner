import sys
import time
import threading
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from quest_api import DiscordAPIWorker
from spoof_engine import SpoofEngine
from logger import sys_log, log
from i18n import t

class CLIApp:
    def __init__(self):
        self.console = Console()
        self.games = []
        self.filtered_games = []
        self.worker_finished = False
        self.active_engines = {} # game_id -> engine
        self.logs = []
        
        def on_log(msg):
            self.logs.append(msg)
            if len(self.logs) > 50:
                self.logs.pop(0)
        sys_log.subscribe(on_log)

    def on_status(self, msg):
        pass

    def on_data(self, data):
        self.games = data
        for i, g in enumerate(self.games):
            g['global_index'] = i + 1
        self.filtered_games = self.games.copy()
        self.worker_finished = True

    def run(self):
        self.console.clear()
        
        # Ask language first
        lang_choice = Prompt.ask("Choose language / Выберите язык (en/ru)", choices=["en", "ru"], default="ru")
        t.set_lang(lang_choice)
        
        self.console.clear()
        self.console.print(Panel.fit(f"[bold blue]{t.get('title')}[/bold blue]", border_style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            progress.add_task(description=t.get("fetch"), total=None)
            worker = DiscordAPIWorker(self.on_data, self.on_status)
            worker.start()
            
            while not self.worker_finished:
                time.sleep(0.1)

        self.console.print(f"[green]{t.get('log_fetch_success', len(self.games))}[/green]\n")
        self.main_loop()

    def main_loop(self):
        while True:
            action = Prompt.ask(
                f"\n[bold]{t.get('cli_choose_action')}[/bold]", 
                choices=["search", "list", "active", "logs", "lang", "quit"], 
                default="search"
            )

            if action == "quit":
                for engine in self.active_engines.values():
                    engine.stop()
                break
            elif action == "lang":
                lang_choice = Prompt.ask(t.get("cli_choose_lang") + " (en/ru)", choices=["en", "ru"], default="ru")
                t.set_lang(lang_choice)
            elif action == "active":
                self.display_active()
            elif action == "logs":
                self.display_logs()
            elif action == "list":
                self.filtered_games = self.games[:50]
                self.display_games()
                self.select_game()
            elif action == "search":
                query = Prompt.ask(t.get("cli_search_game"))
                self.filtered_games = [g for g in self.games if query.lower() in g['title'].lower()]
                if not self.filtered_games:
                    self.console.print(f"[red]{t.get('cli_no_games')}[/red]")
                else:
                    self.display_games()
                    self.select_game()

    def display_active(self):
        self.console.print(f"\n[bold green]{t.get('cli_active_games')}[/bold green]")
        if not self.active_engines:
            self.console.print(f"[yellow]{t.get('cli_no_active')}[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold green")
        table.add_column("IDX", style="dim", width=6)
        table.add_column("Title")
        table.add_column("Time")
        table.add_column("Exe")
        
        keys = list(self.active_engines.keys())
        for idx, gid in enumerate(keys):
            engine = self.active_engines[gid]
            table.add_row(str(idx + 1), engine.meta['title'], engine.get_runtime_str(), engine.chosen_exe)
            
        self.console.print(table)
        
        stop_idx = IntPrompt.ask(f"\n[cyan]{t.get('cli_stop_prompt')}[/cyan]", default=0)
        if stop_idx > 0 and stop_idx <= len(keys):
            gid_to_stop = keys[stop_idx - 1]
            self.active_engines[gid_to_stop].stop()
            del self.active_engines[gid_to_stop]

    def display_logs(self):
        self.console.print(f"\n[bold blue]{t.get('cli_sys_log')}[/bold blue]")
        for l in self.logs[-20:]:
            self.console.print(f"[dim]{l}[/dim]")

    def display_games(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Title")
        table.add_column("Executables")
        
        limit = min(50, len(self.filtered_games))
        for i in range(limit):
            g = self.filtered_games[i]
            exes = ", ".join(g.get("exes", [])[:2])
            if len(g.get("exes", [])) > 2:
                exes += "..."
            table.add_row(str(i + 1), g['title'], exes)
            
        self.console.print(table)
        if len(self.filtered_games) > 50:
            self.console.print(f"[dim]{t.get('more_games', len(self.filtered_games) - 50)}[/dim]")

    def select_game(self):
        self.console.print(f"\n[cyan]{t.get('cli_enter_id')}[/cyan]")
        limit = min(50, len(self.filtered_games))
        choice = IntPrompt.ask("ID", default=0)
        
        if choice > 0 and choice <= limit:
            game_meta = self.filtered_games[choice - 1]
            self.run_spoofer(game_meta)

    def run_spoofer(self, meta):
        execs = meta.get("exes", ["game.exe"])
        chosen_exe = execs[0]
        if len(execs) > 1:
            self.console.print("Available executables:")
            for i, exe in enumerate(execs):
                self.console.print(f"  {i + 1}. {exe}")
            exe_choice = IntPrompt.ask("Select executable index", default=1)
            if 1 <= exe_choice <= len(execs):
                chosen_exe = execs[exe_choice - 1]
                
        window_title = Prompt.ask(t.get("settings_window") + " (Press enter for default)", default=meta['title'])
                
        gid = meta['id']
        if gid in self.active_engines:
            self.active_engines[gid].stop()
            
        engine = SpoofEngine(meta)
        success = engine.start(chosen_exe, window_title)
        
        if success:
            self.active_engines[gid] = engine
            self.console.print(f"[bold green]Process Spoofing Active in background![/bold green] (Exe: {chosen_exe})")
        else:
            self.console.print("[bold red]Failed to start spoofing process.[/bold red]\n")

if __name__ == "__main__":
    app = CLIApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
