r"""
Automated File Organizer.

Sorts the files directly inside a folder (for example Downloads) into
category subfolders - Documents, Images, Videos, Archives and Code -
based on their extension. Files are never overwritten: if a name is
already used, the file gets a free name like 'report (1).pdf'.
Everything that happens is shown on screen and written to organizer.log.

How to run:
    python organizer.py "C:\Users\you\Downloads" --dry-run   (preview only)
    python organizer.py "C:\Users\you\Downloads"             (really move)
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

# ===== Settings =====
BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "organizer.log"

# One logger for the whole program: it writes to the screen and to organizer.log
logger = logging.getLogger("organizer")

# Extension -> category folder. Extensions are written in lowercase.
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".ppt": "Documents", ".pptx": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".svg": "Images", ".webp": "Images", ".heic": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos",
    ".wmv": "Videos", ".webm": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives",
    # Code
    ".py": "Code", ".ipynb": "Code", ".js": "Code", ".html": "Code",
    ".css": "Code", ".json": "Code", ".c": "Code", ".cpp": "Code",
    ".h": "Code", ".java": "Code", ".ino": "Code",
}


# ===== Functions =====
def get_category(file_name):
    """Return the category folder for a file name, or None if the extension is not known."""
    extension = Path(file_name).suffix.lower()
    return EXTENSION_MAP.get(extension)


def plan_moves(folder):
    """Look at the files directly inside folder (not in subfolders).

    Return two lists:
      moves:   (file_path, category) for every file that should be moved
      skipped: (name, reason) for everything that stays where it is
    """
    moves = []
    skipped = []
    this_script = Path(__file__).resolve()

    with os.scandir(folder) as entries:
        for entry in sorted(entries, key=lambda e: e.name.lower()):
            file_path = Path(entry.path)

            if not entry.is_file(follow_symlinks=False):
                skipped.append((entry.name, "folder or shortcut"))
            elif file_path.resolve() == this_script:
                skipped.append((entry.name, "this program itself"))
            else:
                category = get_category(entry.name)
                if category is None:
                    skipped.append((entry.name, "unknown extension"))
                else:
                    moves.append((file_path, category))

    return moves, skipped


def get_unique_path(folder, file_name):
    """Return a path in folder that is not used yet.

    report.pdf -> report.pdf if free,
               -> report (1).pdf if report.pdf already exists,
               -> report (2).pdf if that also exists, and so on.
    """
    target = folder / file_name
    if not target.exists():
        return target

    stem = Path(file_name).stem      # "report"
    suffix = Path(file_name).suffix  # ".pdf"
    counter = 1
    while True:
        target = folder / f"{stem} ({counter}){suffix}"
        if not target.exists():
            return target
        counter += 1


def move_file(file_path, category, base_folder):
    """Move one file into its category folder and return the new path.

    The category folder is created only when it is needed.
    If the name is already used there, a free name like 'report (1).pdf' is chosen.
    """
    category_folder = base_folder / category
    category_folder.mkdir(exist_ok=True)

    destination = get_unique_path(category_folder, file_path.name)
    try:
        shutil.move(file_path, destination)
    except OSError:
        # On Windows, shutil.move() may copy a locked file first and only then fail
        # to delete the original. Remove that half-finished copy so nothing is duplicated.
        if file_path.exists() and destination.exists():
            destination.unlink()
        raise
    return destination


def organize(folder, dry_run=False):
    """Organize the files directly inside folder into category folders.

    With dry_run=True nothing is moved: the plan is only shown.
    One problem file never stops the whole run: it is reported and the next file is handled.
    """
    items_found = len(os.listdir(folder))   # counted separately, used as a cross-check
    moves, skipped = plan_moves(folder)
    moved = []
    failed = []

    mode = "DRY RUN (nothing will be moved)" if dry_run else "Organizing"
    logger.info(f"{mode}: {folder}")

    for file_path, category in moves:
        if dry_run:
            # Show the name the file WOULD get, without creating folders or moving anything
            destination = get_unique_path(folder / category, file_path.name)
            moved.append((file_path.name, category, destination.name))
            logger.info(f"  WOULD MOVE {file_path.name:<25} -> {category}{os.sep}{destination.name}")
            continue

        try:
            destination = move_file(file_path, category, folder)
        except PermissionError:
            failed.append((file_path.name, "file is in use or access is denied"))
            logger.warning(f"  FAILED {file_path.name:<25} (file is in use or access is denied)")
        except OSError as error:
            failed.append((file_path.name, error.strerror or str(error)))
            logger.warning(f"  FAILED {file_path.name:<25} ({error.strerror or error})")
        else:
            moved.append((file_path.name, category, destination.name))
            logger.info(f"  MOVED  {file_path.name:<25} -> {category}{os.sep}{destination.name}")

    for name, reason in skipped:
        logger.info(f"  SKIP   {name:<25} ({reason})")

    return items_found, moved, skipped, failed


def print_summary(folder, items_found, moved, skipped, failed, dry_run=False):
    """Log a formatted summary of what happened in this run."""
    accounted = len(moved) + len(skipped) + len(failed)

    # Count the moved files per category, e.g. {"Documents": 5, "Images": 3}
    per_category = {}
    for name, category, new_name in moved:
        per_category[category] = per_category.get(category, 0) + 1

    # Files that got a new name like 'report (1).pdf'
    renamed = [(name, new_name) for name, category, new_name in moved if name != new_name]

    title = "EXECUTION SUMMARY (DRY RUN - nothing was moved)" if dry_run else "EXECUTION SUMMARY"
    relocated_label = "Would be relocated" if dry_run else "Files relocated"

    line = "=" * 50
    logger.info("")
    logger.info(line)
    logger.info(title)
    logger.info(line)
    logger.info(f"Folder            : {folder}")
    logger.info(f"Items found       : {items_found}")
    logger.info("-" * 50)
    logger.info(f"{relocated_label:<18}: {len(moved)}")
    for category in sorted(per_category):
        logger.info(f"  {category:<15} : {per_category[category]}")
    logger.info(f"Renamed           : {len(renamed)} (name was already used)")
    logger.info(f"Skipped           : {len(skipped)}")
    logger.info(f"Failed            : {len(failed)}")
    for name, reason in failed:
        logger.info(f"  {name} ({reason})")
    logger.info("-" * 50)
    status = "OK" if accounted == items_found else "MISMATCH - please check the folder"
    verb = "to move" if dry_run else "moved"
    logger.info(f"Check: {len(moved)} {verb} + {len(skipped)} skipped + {len(failed)} failed "
                f"= {accounted} of {items_found} items -> {status}")
    logger.info(line)


def setup_logging():
    """Send log messages to the screen (short) and to organizer.log (with date and time)."""
    logger.setLevel(logging.INFO)

    screen = logging.StreamHandler(sys.stdout)   # normal output, not the error channel
    screen.setFormatter(logging.Formatter("%(message)s"))

    log_file = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    log_file.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                                            datefmt="%Y-%m-%d %H:%M:%S"))

    logger.addHandler(screen)
    logger.addHandler(log_file)


def parse_arguments():
    """Read the folder and options given on the command line."""
    parser = argparse.ArgumentParser(
        description="Sort the files in a folder into Documents, Images, Videos, "
                    "Archives and Code subfolders, based on their extension.")
    parser.add_argument("folder", help="the folder to organize, e.g. your Downloads folder")
    parser.add_argument("--dry-run", action="store_true",
                        help="only show what would be moved, without moving anything")
    return parser.parse_args()


def check_folder(folder):
    """Return an error message if folder cannot be organized, or None if it is fine."""
    if not folder.exists():
        return f"Folder not found: {folder}"
    if not folder.is_dir():
        return f"This is a file, not a folder: {folder}"
    if folder == BASE_DIR.resolve():
        return "Refusing to organize the organizer's own folder (its files would be moved)."
    return None


def main():
    args = parse_arguments()
    folder = Path(args.folder).resolve()

    setup_logging()

    problem = check_folder(folder)
    if problem:
        logger.error(f"Error: {problem}")
        sys.exit(1)

    try:
        items_found, moved, skipped, failed = organize(folder, dry_run=args.dry_run)
    except PermissionError:
        logger.error(f"Error: no permission to read the folder: {folder}")
        sys.exit(1)

    print_summary(folder, items_found, moved, skipped, failed, dry_run=args.dry_run)


# ===== Program entry point =====
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Stopped by the user (Ctrl+C). Files that were already moved stay "
                       "in their new folders - see organizer.log for the details.")
        sys.exit(1)