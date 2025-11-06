import os
from pathlib import Path
import sys
import time
import shutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return  # ignore new folders

        file_path = event.src_path
        print(f"New file detected: {file_path}")

        #print("func",sys.argv[2])
        #print("dest",sys.argv[3])

        if(sys.argv[2] == "move"):

            if(sys.argv[4]):
                if(Path(file_path).suffix != f".{sys.argv[4]}"):
                    print(f".{Path(file_path).suffix}: not processed")
                    return
            try:
                shutil.move(file_path, sys.argv[3])
                print(f"Moved {file_path} → {sys.argv[3]}")
            except Exception as e:
                print(f"Error moving file: {e}")

        elif(sys.argv[2] == ""):
            pass

        # Example 1: Move the file somewhere
        """ dest_dir = "processed"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        try:
            shutil.move(file_path, dest_path)
            print(f"Moved {file_path} → {dest_path}")
        except Exception as e:
            print(f"Error moving file: {e}") """

        # Example 2: Or rename the file instead
        # new_name = f"renamed_{os.path.basename(file_path)}"
        # new_path = os.path.join(os.path.dirname(file_path), new_name)
        # os.rename(file_path, new_path)
        # print(f"Renamed {file_path} → {new_path}")


if __name__ == "__main__":
    print("\nFile automation\n")
    path_to_watch = sys.argv[1] #input("\nPath to watch: ")
    if not path_to_watch:
        path_to_watch = "."
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()

    print(f"Watching directory: {os.path.abspath(path_to_watch)}")

    print("func",sys.argv[2])
    print("value",sys.argv[3])

    if(sys.argv[4]):
        print("format: ",sys.argv[4])

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
