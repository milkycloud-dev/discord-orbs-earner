import threading
import time

class SystemLogger:
    def __init__(self):
        self.logs = []
        self.subscribers = []
        self._lock = threading.Lock()
        
    def add_log(self, key, *args):
        """Add a log event with a timestamp and notify all subscribers."""
        timestamp = time.strftime("[%H:%M:%S]")
        event = {"timestamp": timestamp, "key": key, "args": args}
        
        with self._lock:
            self.logs.append(event)
            # Keep only the last 100 logs in memory
            if len(self.logs) > 100:
                self.logs.pop(0)
                
            for sub in self.subscribers:
                try:
                    sub(event)
                except:
                    pass

    def subscribe(self, callback):
        """Add a callback function to be called whenever a new log is added."""
        with self._lock:
            if callback not in self.subscribers:
                self.subscribers.append(callback)
                
    def unsubscribe(self, callback):
        with self._lock:
            if callback in self.subscribers:
                self.subscribers.remove(callback)

# Global logger instance
sys_log = SystemLogger()

def log(key, *args):
    sys_log.add_log(key, *args)
