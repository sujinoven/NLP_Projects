import io
import json
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Handler, ThreadingHTTPServer
from engine import generate
from import_bundle import import_bundle
from preprocessing import clean_article


class Tests(unittest.TestCase):
    def test_cleaning_matches_training(self):
        self.assertEqual(clean_article('Reported.Sources  &amp; “News” https://example.com'), 'reported. sources & "news"')

    def test_invalid_inputs_before_loading(self):
        for text, count in [('', 10), ('hello', 0), ('hello', True), ('x'*3001, 1)]:
            with self.assertRaises(ValueError):
                generate(text, count)

    def test_import_ignores_executable_and_traversal_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root/'bundle.zip'
            with zipfile.ZipFile(source, 'w') as archive:
                archive.writestr('best_gru.keras', b'test fixture, not a model')
                archive.writestr('tokenizer.json', '{}')
                archive.writestr('config.json', json.dumps({'padding':'post','truncating':'pre'}))
                archive.writestr('../escape.txt', 'no')
                archive.writestr('preprocessing.py', 'raise RuntimeError()')
            import_bundle(source, root/'models')
            self.assertEqual(len(list((root/'models').iterdir())), 3)
            self.assertFalse((root/'escape.txt').exists())

    def test_http_routes_and_prediction_contract(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            for route in ['/', '/app.js', '/style.css', '/api/status']:
                with urllib.request.urlopen(base+route) as response:
                    self.assertEqual(response.status, 200)
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(base+'/../engine.py')
            self.assertEqual(error.exception.code, 404)
            expected = {'text':'hello world','steps':[], 'suggestions':[], 'warnings':[]}
            with patch('engine.generate', return_value=expected) as mocked:
                request = urllib.request.Request(base+'/api/generate', data=json.dumps({'text':'hello','count':1}).encode(), headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(request) as response:
                    self.assertEqual(json.load(response), expected)
                mocked.assert_called_once_with('hello', 1)
            request = urllib.request.Request(base+'/api/generate', data=b'[]', headers={'Content-Type':'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
