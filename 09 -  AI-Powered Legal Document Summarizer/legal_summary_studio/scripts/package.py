"""Rebuild a source-only ZIP; SDKs, caches, secrets and model weights stay out."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib

root = Path(__file__).resolve().parents[1]
output = root.parent / "outputs"
output.mkdir(exist_ok=True)
archive = output / "Legal-Summary-Studio-Flutter-Flask.zip"
excluded = {".git", ".venv", "__pycache__", ".pytest_cache", ".dart_tool", "build", ".model_cache"}

with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in excluded for part in relative.parts):
            continue
        if path.name == ".env" or path.suffix in {".pyc", ".log"}:
            continue
        bundle.write(path, Path(root.name) / relative)

with ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    names = bundle.namelist()
    for required in ("README.md", "backend/run.py", "frontend/pubspec.yaml", "frontend/lib/main.dart", "docs/VALIDATION.md"):
        assert f"{root.name}/{required}" in names, required

digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
print(f"Created {archive}\nFiles: {len(names)}\nBytes: {archive.stat().st_size}\nSHA256: {digest}")
