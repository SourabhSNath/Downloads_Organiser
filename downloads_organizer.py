import shutil
import time
from pathlib import Path
from os import listdir

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from file_extensions import file_formats

# Downlaods folder path
DOWNLOADS = Path.home().joinpath("Downloads")


# Class extending FileSystemEventHandler, override on_modified()
class DownloadsObserver(FileSystemEventHandler):

    # Automatically called when the downloads folder is modified in some way
    def on_modified(self, event):
        self.start_file_organiser()

    def start_file_organiser(self):
        for file_name in listdir(DOWNLOADS):

            source = DOWNLOADS.joinpath(file_name)
            exten = Path(file_name).suffix  # Get Extension

            if file_formats.__contains__(exten):

                # Path towards the FileExtension's folder
                new_path = DOWNLOADS.joinpath(file_formats[exten])

                # Make the folder if it doesn't exist
                new_path.mkdir(exist_ok=True)

                # Move the source file to the new_path/file location
                destination = new_path.joinpath(file_name)
                if Path(destination).exists():
                    new_file_path = self.check_file_exists(destination, exten)
                    shutil.move(source, new_file_path)
                else:
                    shutil.move(source, destination)

    # Recursively check and rename if the new file name exists
    def check_file_exists(self, destination, exten):
        file_without_exten = Path(destination).with_suffix("")

        # Check if the new destination exists
        if Path(destination).exists():
            # Append (copy) if the file name exists
            file_renamed_path = Path(
                str(file_without_exten) + "(copy)" + exten)
            return self.check_file_exists(file_renamed_path, exten)
        else:
            return destination

###############################################################


downloads_event_observer = DownloadsObserver()

# Start cleaning up the folders right away
downloads_event_observer.start_file_organiser()

observer = Observer()
observer.schedule(downloads_event_observer, DOWNLOADS, recursive=False)
observer.start()
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()
except Exception as e:
    print(e)
    observer.stop()
observer.join()
