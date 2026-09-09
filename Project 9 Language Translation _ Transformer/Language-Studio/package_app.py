"""Create a portable source ZIP, deliberately excluding weights and environments."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
files = [
    "app.py", "engine.py", "protection.py", "requirements.txt", "requirements-lock.txt",
    "README.md", "VALIDATION.md", "start.ps1", "smoke_test.py", "package_app.py",
    ".gitignore", ".streamlit/config.toml", "tests/test_engine.py", "tests/test_app.py",
]
destination = root / "Language-Studio.zip"
with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(root / name, "Language-Studio/" + name)
with ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(files)
print(f"Created {destination.name}: {destination.stat().st_size:,} bytes, {len(files)} files")
