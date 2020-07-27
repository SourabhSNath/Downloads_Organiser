import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from file_extensions import file_formats, EXTENSIONS

# Downlaods folder path
DOWNLOADS = Path.home().joinpath("Downloads")


# Class extending FileSystemEventHandler, override on_modified()
class DownloadsObserver(FileSystemEventHandler):

    """
     Automatically called when the downloads folder is modified in some way

     param event:
            Event representing file/directory modification.
    """

    def on_modified(self, event):
        # print(f'on_modified, path : {event.src_path}')

        if self.is_download_finished():
            time.sleep(2)  # wait to allow file to be fully written
            self.start_file_organiser()

    """
    Returns true if all parts of the file were downloaded successfully

    .part and .crdownload are parts of the file being downloaded, usually seen when the
            downloaded file is too big to be downloaded as whole
            
    big zip files from github are downloaded in parts.
    """

    def is_download_finished(self):
        firefox_temp_file = sorted(Path(DOWNLOADS).glob('*.part'))
        chrome_temp_file = sorted(Path(DOWNLOADS).glob('*.crdownload'))
        downloaded_files = sorted(Path(DOWNLOADS).glob('*.*'))

        # The lengths become 0 when the parts combine into the file
        if len(firefox_temp_file) == 0 \
                and len(chrome_temp_file) == 0 \
                and len(downloaded_files) >= 1:
            return True
        else:
            return False

    # Start organising the files
    def start_file_organiser(self):
        for file_name in os.listdir(DOWNLOADS):

            source = DOWNLOADS.joinpath(file_name)
            exten = Path(file_name).suffix  # Get Extension

            if Path(source).is_dir() and file_name not in EXTENSIONS.keys():
                exten_folder_path = DOWNLOADS.joinpath("Folders")
                self.mkdir_and_move(
                    file_name, exten, source, exten_folder_path)

            if Path(source).is_file() and (exten != ".part" or exten != ".crdownload"):
                exten_folder_path = DOWNLOADS.joinpath(file_formats[exten])
                self.mkdir_and_move(
                    file_name, exten, source, exten_folder_path)

    """
     Make the dir and move the files after checking if the files exist in the destination

     params:
        file_name: The downloaded file's or folder's name
        exten: File extension
        source: Download location of the file or folder
        exten_folder_path: Location of the folder made for the file's type
    """

    def mkdir_and_move(self, file_name, exten, source, exten_folder_path):

        # Make the folder if it doesn't exist
        exten_folder_path.mkdir(exist_ok=True)

        # Move the source file to the new_path/file location
        destination = exten_folder_path.joinpath(file_name)
        if Path(destination).exists():
            new_file_path = self.check_file_exists(destination, exten)
            shutil.move(source, new_file_path)
        else:
            shutil.move(source, destination)

    """
     Recursively check and rename if the new file name exists

     parmas:
        destination: the destination where the file should be moved to
        exten: file extension
    """

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

# Keyboard interrupt ctrl + c is used to stop the script
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Stopped Observing Downloads")
    observer.stop()
observer.join()
