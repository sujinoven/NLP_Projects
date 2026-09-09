"""UI interaction checks. No model weights are loaded by these tests."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit is not installed")
class AppTests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()

    def test_initial_page_and_empty_submission(self):
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.text_input), 0)
        self.assertIn("translation", self.app.title[0].value)
        self.app.button[3].click().run()
        self.assertTrue(self.app.error)
        self.assertFalse(self.app.exception)

    def test_automatic_protection_preview_without_prefilled_brand(self):
        self.assertFalse(any("FlyRank" in item.value for item in self.app.text))
        self.app.text_area(key="message").set_value("My CloudDesk account shows E403.").run()
        preview = " ".join(item.value for item in self.app.text)
        self.assertIn("CloudDesk", preview)
        self.assertIn("E403", preview)
        self.assertEqual(len(self.app.text_input), 0)

    def test_code_only_and_clear(self):
        self.app.text_area(key="message").set_value("E403")
        self.app.button[3].click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["result"]["translation"], "E403")
        self.assertEqual(len(self.app.get("download_button")), 2)
        self.app.button[4].click().run()
        self.assertEqual(self.app.text_area(key="message").value, "")

    def test_example_and_stale_output(self):
        self.app.button[0].click().run()
        self.assertIn("password", self.app.text_area(key="message").value)
        self.app.selectbox(key="source").select("English")
        self.app.selectbox(key="target").select("French")
        with patch("engine.NllbBackend.translate_many", return_value=["Aidez-moi à réinitialiser mon mot de passe."]):
            self.app.button[3].click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.text_area), 2)
        self.app.text_area(key="message").set_value("Different message").run()
        self.assertEqual(len(self.app.text_area), 1)


if __name__ == "__main__":
    unittest.main()
