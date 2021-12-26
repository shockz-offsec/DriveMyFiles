from win10toast import ToastNotifier
import pathlib
from backup import recompile
from utils import check_space_availability


def show_toast_task(title, message, path_image):
    toaster = ToastNotifier()
    toaster.show_toast(title,
                       message,
                       duration=10, icon_path=path_image)


if __name__ == "__main__":

    try:
        working_directory = str(pathlib.Path(
            __file__).parent.absolute().parent.absolute())+"\\Resources\\icon.ico"
        if(check_space_availability() == False):
            working_directory = str(pathlib.Path(
            __file__).parent.absolute().parent.absolute())+"\\Resources\\error.ico"
            show_toast_task("Problem with DriveMyFiles",
                            "There is not enough space in drive", working_directory)
        else:
            output = recompile()
            show_toast_task(
                "DriveMyFiles", "Backup successfully", working_directory)

    except (OSError, IndexError, FileNotFoundError) as e:

        working_directory = str(pathlib.Path(
            __file__).parent.absolute().parent.absolute())+"\\Resources\\error.ico"
        show_toast_task(" Error in DriveMyFiles",
                        "An error occurred in the automatic backup", working_directory)
