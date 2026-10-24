"""
Create a messy test folder full of small dummy files for testing organizer.py.

The organizer only looks at file names and extensions, not at the content,
so tiny text files with the right names are enough for testing.

This script never deletes anything. It only creates the test folder
and writes dummy files into it.

How to run:
    python create_test_folder.py
"""

from pathlib import Path

# The test folder is created next to this script
BASE_DIR = Path(__file__).parent
TEST_FOLDER = BASE_DIR / "test_downloads"

# Dummy files in the main test folder, with the result we expect from the organizer
DUMMY_FILES = [
    # Documents
    "laporan_KTI.pdf",
    "catatan.final.docx",     # several dots in the name
    "nilai_semester.xlsx",
    "notes.txt",
    "Presentasi_Sidang.PPTX", # uppercase extension
    # Images
    "Foto_Wisuda.JPG",        # uppercase extension
    "diagram_kontrol.png",
    "logo.svg",
    # Videos
    "video_jetbot.mp4",
    "rekaman_uji.MOV",
    # Archives
    "backup_proyek.tar.gz",   # double extension
    "library.zip",
    # Code
    "kontroler.py",
    "index.html",
    "blink_led.ino",
    # Should be SKIPPED (left where they are)
    "README",                 # no extension
    "setup.exe",              # not in any category
    "lagu_favorit.mp3",       # not in any category
    "film.mp4.crdownload",    # unfinished Chrome download
    "dokumen.pdf.part",       # unfinished Firefox download
]

# A project folder that must stay untouched (the organizer does not go into subfolders)
PROJECT_FOLDER = TEST_FOLDER / "Proyek_JetBot"
PROJECT_FILES = ["kbbc_controller.py", "data_uji.csv", "foto_robot.jpg"]


def write_dummy_file(path):
    """Write a tiny text file so the file exists with the right name."""
    path.write_text(f"Dummy test file: {path.name}\n", encoding="utf-8")


def main():
    TEST_FOLDER.mkdir(exist_ok=True)
    PROJECT_FOLDER.mkdir(exist_ok=True)

    for name in DUMMY_FILES:
        write_dummy_file(TEST_FOLDER / name)

    for name in PROJECT_FILES:
        write_dummy_file(PROJECT_FOLDER / name)

    print(f"Test folder ready: {TEST_FOLDER}")
    print(f"  {len(DUMMY_FILES)} dummy files in the main folder")
    print(f"  {len(PROJECT_FILES)} dummy files in {PROJECT_FOLDER.name}/ (must stay untouched)")


if __name__ == "__main__":
    main()