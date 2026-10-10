"""Import only data files; never execute Python code from a bundle."""
import argparse
import json
import zipfile
from pathlib import Path


def import_bundle(path, destination):
    names = ['best_gru.keras', 'tokenizer.json', 'config.json']
    with zipfile.ZipFile(path) as archive:
        for name in names:
            if archive.namelist().count(name) != 1:
                raise ValueError(f'The ZIP must contain exactly one {name} at its root.')
            if archive.getinfo(name).file_size > 200 * 1024 * 1024:
                raise ValueError(f'{name} exceeds the 200 MB limit.')
        data = {name: archive.read(name) for name in names}
    config = json.loads(data['config.json'])
    json.loads(data['tokenizer.json'])
    if config.get('padding') != 'post' or config.get('truncating') != 'pre':
        raise ValueError('Expected the right-padded GRU bundle.')
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in data.items():
        (destination / name).write_bytes(content)
    print('Imported GRU model, tokenizer, and settings.')
    print('Training TensorFlow version:', config.get('tensorflow_version', 'not recorded'))
    print('Restart app.py if it is already running.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    args = parser.parse_args()
    import_bundle(args.bundle, Path(__file__).resolve().parent / 'models')
