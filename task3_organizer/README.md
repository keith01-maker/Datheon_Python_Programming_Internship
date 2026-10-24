# Automated File Organizer

A command-line automation script written in Python 3 that organizes a cluttered folder (for example Downloads). It looks at the extension of every file directly inside the folder, creates category subfolders when they are needed, and safely moves each file into its category. Files are never overwritten, problem files never stop the run, and everything is shown on screen and written to a log file.

## Features

| Task requirement | Implementation |
|---|---|
| Inspect every file's extension | `get_category()` with the `EXTENSION_MAP` dictionary |
| Dynamically create category subfolders | `move_file()` creates `Documents`, `Images`, `Videos`, `Archives` or `Code` only when a file needs it |
| Use `os.scandir()` and `shutil.move()` | `plan_moves()` scans the folder, `move_file()` moves the files |
| Handle permission exceptions | `PermissionError` is caught per file; the file is reported and the next file is handled |
| Handle naming collisions | `get_unique_path()` picks a free name such as `report (1).pdf` before moving |
| Formatted execution summary with total files relocated | `print_summary()` |
| Logging output | Every action is shown on screen and appended to `organizer.log` with date and time |

**Extras:**
- `--dry-run` mode that shows exactly what would happen without moving anything
- A cross-check that every item in the folder was accounted for
- `create_test_folder.py` to build a safe test folder full of dummy files

## Requirements

- Python 3.8 or newer (tested with Python 3.13)
- Standard library only (`argparse`, `logging`, `os`, `shutil`, `sys`, `pathlib`), nothing to install

## Files

```
task3_organizer/
├── organizer.py            # the organizer
├── create_test_folder.py   # creates test_downloads/ with dummy files
└── README.md
```

`test_downloads/` and `organizer.log` are created when the scripts run and are not part of the repository.

## How to run

From the repository root. Always preview first with `--dry-run`:

```bash
python task3_organizer/organizer.py "C:\Users\you\Downloads" --dry-run
python task3_organizer/organizer.py "C:\Users\you\Downloads"
```

Put the folder in quotes if its path contains spaces. Show the help with:

```bash
python task3_organizer/organizer.py -h
```

## Try it safely with dummy files

```bash
python task3_organizer/create_test_folder.py
python task3_organizer/organizer.py task3_organizer/test_downloads --dry-run
python task3_organizer/organizer.py task3_organizer/test_downloads
```

`create_test_folder.py` creates 20 small dummy files (plus a `Proyek_JetBot/` project folder) that cover every case: upper-case extensions, names with several dots, unknown extensions, files without an extension and unfinished downloads. The organizer only looks at names and extensions, so dummy files behave exactly like real ones. Run `create_test_folder.py` again (without deleting anything) to test naming collisions.

## Example output

```
Organizing: E:\...\task3_organizer\test_downloads
  MOVED  backup_proyek.tar.gz      -> Archives\backup_proyek.tar.gz
  MOVED  Foto_Wisuda.JPG           -> Images\Foto_Wisuda.JPG
  MOVED  laporan_KTI.pdf           -> Documents\laporan_KTI.pdf
  ...
  SKIP   film.mp4.crdownload       (unknown extension)
  SKIP   Proyek_JetBot             (folder or shortcut)
  SKIP   setup.exe                 (unknown extension)

==================================================
EXECUTION SUMMARY
==================================================
Folder            : E:\...\task3_organizer\test_downloads
Items found       : 21
--------------------------------------------------
Files relocated   : 15
  Archives        : 2
  Code            : 3
  Documents       : 5
  Images          : 3
  Videos          : 2
Renamed           : 0 (name was already used)
Skipped           : 6
Failed            : 0
--------------------------------------------------
Check: 15 moved + 6 skipped + 0 failed = 21 of 21 items -> OK
==================================================
```

## Categories

| Folder | Extensions |
|---|---|
| Documents | `.pdf .doc .docx .txt .rtf .odt .xls .xlsx .csv .ppt .pptx` |
| Images | `.jpg .jpeg .png .gif .bmp .svg .webp .heic` |
| Videos | `.mp4 .mkv .avi .mov .wmv .webm` |
| Archives | `.zip .rar .7z .tar .gz` |
| Code | `.py .ipynb .js .html .css .json .c .cpp .h .java .ino` |

Extensions are matched case-insensitively (`.JPG` = `.jpg`). To add a category, add its extensions to `EXTENSION_MAP`; no other code needs to change.

## Design decisions

- **Only the files directly inside the folder are organized.** Existing subfolders (such as a project folder) are left untouched, because sorting their contents would break them apart. This matches `os.scandir()`, which lists one level only.
- **Unknown extensions are left where they are** and reported as skipped. This includes installers (`.exe`), audio files, files without an extension and unfinished downloads (`.crdownload`, `.part`), which must not be moved while the browser is still writing them.
- **Files are never overwritten.** `shutil.move()` does not raise `FileExistsError`: when the destination is a full file path it may silently overwrite an existing file, and when it is a folder it raises `shutil.Error`. The organizer therefore checks the name first with `get_unique_path()` and moves the file to a name that is guaranteed to be free (`report (1).pdf`, `report (2).pdf`, ...). For double extensions only the last part is kept after the number (`backup.tar (1).gz`).
- **Locked files on Windows.** When a file is open in another program, `shutil.move()` can copy it and then fail to delete the original. The organizer removes such a half-finished copy, so a file is never duplicated, and reports the file as failed.
- **One problem file never stops the run.** Errors are handled per file and listed in the summary; running the organizer again retries them.
- **The organizer's own folder is refused**, so its own files are never moved.
- **Every run is logged** to `organizer.log` (appended, with date and time). The log shows exactly which file was moved where, so a move can be undone by hand if needed.

## Error handling

| Situation | Behaviour |
|---|---|
| Folder does not exist / is a file | Clear error message, nothing is moved |
| Folder is the organizer's own folder | Refused, nothing is moved |
| No permission to read the folder | Clear error message, nothing is moved |
| A file is open in another program | Reported as failed, the run continues, no duplicate is left behind |
| A file disappears during the run | Reported as failed, the run continues |
| Name already used in the category folder | The file gets a free name such as `report (1).pdf` |
| Misspelled option (e.g. `--dryrun`) | Rejected by `argparse` before anything happens |
| `Ctrl+C` | Stops with a message; files already moved stay in their new folders (see the log), run again to finish |
