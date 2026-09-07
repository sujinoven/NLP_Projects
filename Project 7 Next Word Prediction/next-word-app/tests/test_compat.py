import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from model_compat import load_compatible_model, strip_empty_quantization


class CompatibilityTests(unittest.TestCase):
    def test_preserves_real_quantization(self):
        cfg = {'layers': [{'quantization_config': None}, {'quantization_config': {'mode': 'int8'}}]}
        self.assertEqual(strip_empty_quantization(cfg), {'layers': [{}, {'quantization_config': {'mode': 'int8'}}]})

    def test_retry_preserves_weights_and_original(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'model.keras'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('config.json', json.dumps({'layers': [{'quantization_config': None, 'units': 128}]}))
                archive.writestr('model.weights.h5', b'unchanged weight fixture')
            original = path.read_bytes()
            calls = []
            def loader(candidate, compile):
                calls.append(candidate)
                self.assertFalse(compile)
                if len(calls) == 1:
                    raise TypeError("Unrecognized keyword arguments: {'quantization_config': None}")
                with zipfile.ZipFile(candidate) as archive:
                    self.assertEqual(json.loads(archive.read('config.json')), {'layers': [{'units': 128}]})
                    self.assertEqual(archive.read('model.weights.h5'), b'unchanged weight fixture')
                return 'loaded fixture'
            self.assertEqual(load_compatible_model(path, loader), 'loaded fixture')
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(len(calls), 2)
            self.assertFalse(Path(calls[1]).exists())

    def test_unrelated_error_not_hidden(self):
        def loader(*args, **kwargs):
            raise ValueError('Unrelated error')
        with self.assertRaisesRegex(ValueError, 'Unrelated error'):
            load_compatible_model('unused', loader)
