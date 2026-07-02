import sys
import os
import argparse
import traceback
import threading
import time
import flet as ft
from quest_api import DiscordAPIWorker
from spoof_engine import SpoofEngine
from logger import sys_log, log
from i18n import t

# --- CLI Entry Point ---
def check_cli():
    parser = argparse.ArgumentParser(description="Discord Orbs Earner")
    parser.add_argument("--cli", action="store_true", help="Run in Command Line Interface mode")
    args, unknown = parser.parse_known_args()

    if args.cli:
        try:
            from cli import CLIApp
            app = CLIApp()
            app.run()
        except Exception as e:
            print(f"CLI Error: {e}")
            traceback.print_exc()
        sys.exit(0)

# --- Flet GUI App ---
def main(page: ft.Page):
    t.set_lang("ru")
    page.title = t.get("title")
    page.theme_mode = ft.ThemeMode.DARK
    page.window.icon = "icon.ico"
    page.window.width = 750
    page.window.height = 700
    page.padding = 20
    page.bgcolor = "#313338"
    
    # State
    all_games = []
    filtered_games = []
    active_engines = {} # game_id -> SpoofEngine
    
    # UI Elements
    title_text = ft.Text(t.get("title"), size=24, weight=ft.FontWeight.BOLD, color="#F2F3F5")
    status_text = ft.Text(t.get("fetch"), size=14, color="#B5BAC1")
    search_field = ft.TextField(
        hint_text=t.get("filter"), 
        expand=True,
        bgcolor="#1E1F22",
        border_color="#1E1F22",
        on_change=lambda e: filter_games(e.control.value)
    )
    
    games_list = ft.ListView(expand=True, spacing=10, auto_scroll=False)
    active_list = ft.ListView(expand=True, spacing=10, auto_scroll=False)
    log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)
    
    progress_ring = ft.ProgressRing(visible=False)
    
    def on_api_status(msg):
        status_text.value = msg
        page.update()

    def on_api_data(data):
        nonlocal all_games, filtered_games
        all_games = data
        filtered_games = data.copy()
        
        status_text.value = t.get("ready", len(data))
        log(t.get("log_fetch_success", len(data)))
        progress_ring.visible = False
        btn_reload.disabled = False
        render_games()
        page.update()
        
    def fetch_quests(e=None):
        progress_ring.visible = True
        btn_reload.disabled = True
        games_list.controls.clear()
        status_text.value = t.get("fetch")
        log(t.get("log_fetching"))
        page.update()
        
        worker = DiscordAPIWorker(on_api_data, on_api_status)
        worker.start()

    def filter_games(query):
        nonlocal filtered_games
        query = query.lower()
        if query:
            log("log_filtering", query)
        filtered_games = [g for g in all_games if query in g['title'].lower()]
        render_games()

    def play_game(game_meta):
        game_id = game_meta['id']
        if game_id not in active_engines:
            engine = SpoofEngine(game_meta)
            engine.start()
            active_engines[game_id] = engine
        render_active_games()
        page.update()
        
    def stop_game(game_id):
        if game_id in active_engines:
            active_engines[game_id].stop()
            del active_engines[game_id]
        render_active_games()
        page.update()
        
    def render_games():
        games_list.controls.clear()
        display_limit = min(200, len(filtered_games))
        
        for i in range(display_limit):
            g = filtered_games[i]
            games_list.controls.append(create_game_tile(g, i + 1))
            
        if len(filtered_games) > display_limit:
            games_list.controls.append(
                ft.Text(t.get("more_games", len(filtered_games) - display_limit), color="#B5BAC1", italic=True)
            )
        page.update()
        
    def render_active_games():
        active_list.controls.clear()
        if not active_engines:
            active_list.controls.append(ft.Text(t.get("cli_no_active"), color="#B5BAC1"))
        
        for gid, engine in active_engines.items():
            active_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(engine.meta['title'], size=16, weight=ft.FontWeight.BOLD, color="#57F287", expand=True),
                        ft.Text(engine.get_runtime_str(), size=14, color="#DBDEE1", data=gid),
                        ft.IconButton(icon=ft.Icons.SETTINGS, tooltip=t.get("btn_settings"), on_click=lambda e, meta=engine.meta: open_settings(meta)),
                        ft.IconButton(icon=ft.Icons.STOP, icon_color="#DA373C", tooltip=t.get("btn_stop"), on_click=lambda e, g=gid: stop_game(g))
                    ]),
                    padding=10,
                    bgcolor="#1E1F22",
                    border_radius=8
                )
            )

    def update_timers_logic():
        stopped_gids = []
        for gid, engine in list(active_engines.items()):
            if not engine.is_running():
                stopped_gids.append(gid)
        
        for gid in stopped_gids:
            engine = active_engines[gid]
            engine.stop()
            del active_engines[gid]
            
        if stopped_gids:
            render_active_games()
            try:
                active_list.update()
                page.update()
            except:
                pass

        for c in active_list.controls:
            if isinstance(c, ft.Container) and isinstance(c.content, ft.Row) and len(c.content.controls) >= 2:
                timer_txt = c.content.controls[1]
                gid = timer_txt.data
                if gid in active_engines:
                    timer_txt.value = active_engines[gid].get_runtime_str()
                    try:
                        timer_txt.update()
                    except:
                        pass

    def create_game_tile(game_meta, index):
        icon_src = game_meta.get("icon_url")
        if not icon_src:
            icon_src = "videogame_asset"
            
        return ft.Container(
            content=ft.Row([
                ft.Image(src=icon_src, width=32, height=32, fit="contain") if isinstance(icon_src, str) and icon_src.startswith("http") else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=32),
                ft.Text(f"{index}. {game_meta['title']}", size=16, color="#DBDEE1", expand=True),
                ft.ElevatedButton(t.get("btn_play"), icon=ft.Icons.PLAY_ARROW, bgcolor="#23A559", color=ft.Colors.WHITE, on_click=lambda e: play_game(game_meta))
            ]),
            padding=10,
            bgcolor="#2B2D31",
            border_radius=8
        )

    # --- Settings Dialog ---
    settings_dialog = ft.AlertDialog(
        modal=True,
        content_padding=20,
        shape=ft.RoundedRectangleBorder(radius=10),
    )
    
    def open_settings(game_meta):
        gid = game_meta['id']
        engine = active_engines.get(gid)
        if not engine:
            return
            
        execs = game_meta.get('exes', ['game.exe'])
        dd_execs = ft.Dropdown(
            options=[ft.dropdown.Option(exe) for exe in execs],
            value=engine.chosen_exe or execs[0],
            bgcolor="#1E1F22",
            border_color="#1E1F22"
        )
        
        txt_window = ft.TextField(
            value=engine.window_title,
            bgcolor="#1E1F22",
            border_color="#1E1F22"
        )
        
        def apply_click(e):
            engine.stop()
            engine.start(chosen_exe=dd_execs.value, window_title=txt_window.value)
            page.pop_dialog()
            render_active_games()
            log("log_settings_apply", game_meta['title'])
            page.update()
            
        def close_click(e):
            page.pop_dialog()
            
        settings_dialog.title = ft.Text(t.get("settings_title", game_meta['title']), weight=ft.FontWeight.BOLD)
        settings_dialog.content = ft.Column([
            ft.Text(t.get("settings_desc"), color="#B5BAC1"),
            ft.Text(t.get("settings_exe"), weight=ft.FontWeight.BOLD),
            dd_execs,
            ft.Text(t.get("settings_window"), weight=ft.FontWeight.BOLD),
            txt_window,
        ], tight=True, spacing=10)
        
        settings_dialog.actions = [
            ft.TextButton(t.get("btn_apply"), on_click=apply_click),
            ft.TextButton(t.get("btn_close"), on_click=close_click)
        ]
        
        log("log_settings_open", game_meta['title'])
        page.show_dialog(settings_dialog)

    def render_logs():
        log_list.controls.clear()
        for event in sys_log.logs:
            msg = event["timestamp"] + " " + t.get(event["key"], *event["args"])
            log_list.controls.append(ft.Text(msg, size=12, color="#B5BAC1", font_family="monospace"))
        
    def update_logs(event):
        msg = event["timestamp"] + " " + t.get(event["key"], *event["args"])
        log_list.controls.append(ft.Text(msg, size=12, color="#B5BAC1", font_family="monospace"))
        if len(log_list.controls) > 100:
            log_list.controls.pop(0)
        try:
            page.update()
        except:
            pass
        
    sys_log.subscribe(update_logs)
    
    # Render logs initially
    render_logs()

    # Change Language
    def change_lang(e):
        try:
            lang_val = e.control.value.lower()
            t.set_lang(lang_val)
            log("log_lang_change", lang_val.upper())
            page.title = t.get("title")
            title_text.value = t.get("title")
            search_field.hint_text = t.get("filter")
            btn_reload.tooltip = t.get("reload")
            status_text.value = t.get("ready", len(all_games)) if all_games else t.get("fetch")
            lbl_active_games.value = t.get("active_games")
            lbl_system_log.value = t.get("system_log")
            render_games()
            render_active_games()
            render_logs()
            page.update()
        except Exception as ex:
            log("log_spoof_fail_err", "Lang Switch", str(ex))

    # --- Layout Assembly ---
    btn_reload = ft.IconButton(icon=ft.Icons.REFRESH, tooltip=t.get("reload"), on_click=fetch_quests, icon_color="#5865F2")
    
    lang_dd = ft.Dropdown(
        options=[ft.dropdown.Option("RU"), ft.dropdown.Option("EN")],
        value="RU",
        width=120,
        bgcolor="#1E1F22",
        border_color="#1E1F22",
        on_change=change_lang
    )
    lang_dd.on_change = change_lang
    
    header = ft.Row([
        title_text,
        progress_ring,
        ft.Container(expand=True),
        lang_dd
    ])
    
    toolbar = ft.Row([
        search_field,
        btn_reload
    ])
    
    lbl_active_games = ft.Text(t.get("active_games"), weight="bold", size=16, color="#F2F3F5")
    lbl_system_log = ft.Text(t.get("system_log"), weight="bold", size=16, color="#F2F3F5")

    active_container = ft.Container(
        content=ft.Column([
            lbl_active_games,
            active_list
        ]),
        padding=10,
        expand=True,
        bgcolor="#2B2D31",
        border_radius=10
    )
    
    logs_container = ft.Container(
        content=ft.Column([
            lbl_system_log,
            log_list
        ]),
        padding=10, 
        expand=True, 
        bgcolor="#000000",
        border_radius=10,
        border=ft.border.Border(
            top=ft.border.BorderSide(1, "#333333"),
            bottom=ft.border.BorderSide(1, "#333333"),
            left=ft.border.BorderSide(1, "#333333"),
            right=ft.border.BorderSide(1, "#333333")
        )
    )
    
    tabs_control = ft.Row([
        active_container,
        logs_container
    ], expand=True)
    
    main_content = ft.Column([
        header,
        toolbar,
        ft.Container(content=games_list, expand=2, bgcolor="#2B2D31", border_radius=10, padding=10),
        ft.Row([status_text], alignment=ft.MainAxisAlignment.END),
        ft.Container(content=tabs_control, expand=1, bgcolor="#2B2D31", border_radius=10)
    ], expand=True)
    
    page.add(main_content)
    
    # Timer thread
    def update_timers():
        while True:
            time.sleep(1)
            if active_engines:
                try:
                    update_timers_logic()
                except Exception as e:
                    log("log_spoof_fail_err", "Timer Loop", str(e))
                    
    threading.Thread(target=update_timers, daemon=True).start()
    
    fetch_quests()

if __name__ == '__main__':
    check_cli()
    ft.app(target=main, assets_dir=".")
