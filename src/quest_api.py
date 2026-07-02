import threading
import json
import requests
import os

class DiscordAPIWorker:
    """
    Worker class responsible for fetching the detectable games database 
    from the Discord API asynchronously.
    """
    def __init__(self, on_data, on_status):
        """
        Initializes the API Worker.
        
        Args:
            on_data (function): Callback function to receive the parsed list of games.
            on_status (function): Callback function to receive status updates.
        """
        self.on_data = on_data
        self.on_status = on_status
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = os.path.join(base_dir, "cache")
        self.save_file = os.path.join(self.save_dir, "detectable.json")
        
        # Ensure the cache directory exists
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except:
                pass

    def start(self):
        """
        Starts the worker in a separate daemon thread to avoid blocking the main UI/CLI.
        """
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        """
        The main execution function of the thread.
        Downloads the latest detectable games JSON from Discord, caches it, 
        and then processes the data. Falls back to offline cache if the network request fails.
        """
        api_endpoint = "https://discordapp.com/api/v9/applications/detectable"
        self.on_status("Connecting to Discord API...")
        
        response_data = None
        try:
            r = requests.get(api_endpoint, timeout=10)
            if r.status_code == 200:
                with open(self.save_file, 'wb') as f:
                    f.write(r.content)
                response_data = r.json()
            else:
                self.on_status(f"HTTP {r.status_code}. Using offline cache mode.")
                response_data = self.read_local()
        except Exception:
            self.on_status("Connection failed. Using offline cache mode.")
            response_data = self.read_local()

        if not response_data:
            self.on_status("No data available to show.")
            self.on_data([])
            return

        self.on_status(f"Analyzing {len(response_data)} records...")
        final_list = []
        
        # Process the raw Discord API response to extract relevant Windows games
        for entry in response_data:
            exe_list = [e['name'] for e in entry.get('executables', []) if e.get('os') == 'win32']
            if not exe_list:
                continue
                
            game_id = entry.get('id')
            icon_hash = entry.get('icon_hash')
            icon_url = None
            if icon_hash:
                icon_url = f"https://cdn.discordapp.com/app-icons/{game_id}/{icon_hash}.png"
                
            final_list.append({
                "title": entry.get('name', 'Unknown App'),
                "id": game_id,
                "exes": exe_list,
                "icon_url": icon_url
            })
            
        self.on_status(f"Ready: {len(final_list)} PC Games found.")
        self.on_data(final_list)

    def read_local(self):
        """
        Reads the cached detectable.json file if network fails.
        
        Returns:
            dict or None: The parsed JSON data if successful, None otherwise.
        """
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
