import os
from pathlib import Path
import sys
import time
import shutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

def wait_until_unlocked(file_path, timeout=60, check_interval=2):

    start = time.time()
    while time.time() - start < timeout:
        try:
            with open(file_path, "rb"):
                return True  # file opened successfully
        except PermissionError:
            print(f"File still locked: {file_path}")
        except FileNotFoundError:
            print(f"File not found during wait: {file_path}")
            return False
        time.sleep(check_interval)
    return False

def wait_for_file_stable(file_path, stable_seconds=5):
    
    last_size = -1
    stable_time = 0

    while stable_time < stable_seconds:
        try:
            current_size = os.path.getsize(file_path)
        except FileNotFoundError:
            return False  # file disappeared
        
        if current_size == last_size:
            stable_time += 1
        else:
            stable_time = 0
            last_size = current_size

        time.sleep(1)

    return True

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, action=None, dest_dir=None, extension=None):
        super().__init__()
        self.action = action or ""
        self.dest_dir = dest_dir or ""
        self.extension = extension or ""

    def handle_action(self, file_path):
        """Perform the configured action (move, rename, etc.) on a file."""

        # Ignore temporary files
        if file_path.endswith(".tmp"):
            print(f"Ignoring temporary file: {file_path}")
            return

        if not wait_until_unlocked(file_path, timeout=120):
            print(f"Timeout: file still locked → skipping {file_path}")
            return

        if not wait_for_file_stable(file_path, stable_seconds=5):
            print(f"File never stabilized → skipping: {file_path}")
            return

        time.sleep(10)

        # If extension filter is set, enforce it
        if self.extension:
            ext = Path(file_path).suffix.lstrip(".")
            if ext.lower() != self.extension.lower():
                print(f"{file_path} skipped — not a .{self.extension} file")
                return

        if self.action == "move":
            try:
                shutil.move(file_path, self.dest_dir)
                print(f"Moved {file_path} → {self.dest_dir}")
            except Exception as e:
                print(f"Error moving file: {e}")

        elif self.action == "rename":
            try:
                new_name = f"renamed_{os.path.basename(file_path)}"
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                print(f"Renamed {file_path} → {new_path}")
            except Exception as e:
                print(f"Error renaming file: {e}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            self.handle_action(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print(f"File moved/renamed: {event.src_path} → {event.dest_path}")
            # If a .tmp file becomes .mp3, handle the new one
            self.handle_action(event.dest_path)


if __name__ == "__main__":
    print("\nFile automation\n\n")

    if len(sys.argv) < 4:
        print("Usage: python script.py <watch_dir> <action> <dest_dir> [extension]")
        sys.exit(1)

    path_to_watch = sys.argv[1]
    action = sys.argv[2]
    dest_dir = sys.argv[3]
    extension = sys.argv[4] if len(sys.argv) > 4 else None

    if not path_to_watch:
        path_to_watch = "."

    event_handler = MyEventHandler(action=action, dest_dir=dest_dir, extension=extension)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()

    print(f"Watching directory: {os.path.abspath(path_to_watch)}...\n")
    print(f"Action: {action}")
    print(f"Destination: {dest_dir}")
    if extension:
        print(f"Extension filter: .{extension}")

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
