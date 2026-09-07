"""Compatibility for newer Keras archives with empty quantization settings."""
import json
import tempfile
import zipfile
from pathlib import Path


def strip_empty_quantization(value):
    if isinstance(value, dict):
        return {key: strip_empty_quantization(item) for key, item in value.items()
                if not (key == 'quantization_config' and item is None)}
    if isinstance(value, list):
        return [strip_empty_quantization(item) for item in value]
    return value


def load_compatible_model(path, loader):
    try:
        return loader(path, compile=False)
    except (TypeError, ValueError) as exc:
        if 'quantization_config' not in str(exc) or 'Unrecognized keyword' not in str(exc):
            raise
    # Only empty metadata is removed. Real quantization settings remain intact.
    # Never modify the original archive or relax Keras safe loading.
    with tempfile.TemporaryDirectory(prefix='next-word-compat-') as folder:
        compatible = Path(folder) / 'compatible.keras'
        with zipfile.ZipFile(path) as source, zipfile.ZipFile(compatible, 'w') as target:
            config = json.loads(source.read('config.json'))
            cleaned = strip_empty_quantization(config)
            if cleaned == config:
                raise ValueError('This model contains non-empty quantization settings. Use the training Keras version.')
            for member in source.infolist():
                data = source.read(member.filename)
                if member.filename == 'config.json':
                    data = json.dumps(cleaned).encode('utf-8')
                target.writestr(member, data)
        return loader(compatible, compile=False)
