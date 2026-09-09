import unittest
from unittest.mock import patch
from engine import TranslationError, protect, restore, translate_message, collect_terms
from protection import detect_items


class FakeBackend:
    def __init__(self, transform=lambda text: text):
        self.transform = transform
        self.calls = []

    def translate_many(self, sentences, source, target):
        self.calls.append((sentences, source, target))
        return [self.transform(sentence) for sentence in sentences]


class EngineTests(unittest.TestCase):
    def test_unlisted_product_names_automatically_detected(self):
        for name in ["FlyRank", "CloudDesk", "BrightPortal"]:
            self.assertIn(name, collect_terms(f"My {name} account shows E403.", []))
        for text, name in [
            ("My Acme account is locked.", "Acme"),
            ("Microsoft Teams app won't open.", "Microsoft Teams"),
            ("Mon compte Aurora est bloqué.", "Aurora"),
            ("Mi cuenta Solara está bloqueada.", "Solara"),
            ("Slack is down.", "Slack"),
            ('The app "उड़ान" failed.', "उड़ान"),
        ]:
            self.assertIn(name, collect_terms(text, []), text)

    def test_technical_formats_detected_without_manual_input(self):
        text = "Error ERR_AUTH_401 on API v2.4.1; email me+support@example.org or visit https://example.org/help?id=42. Ticket 123456."
        terms = collect_terms(text, [])
        for expected in ["ERR_AUTH_401", "API", "v2.4.1", "me+support@example.org", "https://example.org/help?id=42", "123456"]:
            self.assertIn(expected, terms)
        masked, mapping = protect(text, terms)
        self.assertEqual(restore(masked, mapping), text)

    def test_regular_account_vocabulary_and_urgency_not_frozen(self):
        self.assertEqual(detect_items("PLEASE HELP! My account password reset failed. This is urgent!"), [])

    def test_auto_terms_used_by_translation_with_no_supplied_terms(self):
        backend = FakeBackend()
        result = translate_message("My BrightPortal account shows E403 twice: E403.", "English", "Hindi", [], True, backend)
        self.assertEqual(set(result.protected_terms), {"BrightPortal", "E403"})
        self.assertEqual(result.translation.count("E403"), 2)
        self.assertNotIn("BrightPortal", " ".join(backend.calls[0][0]))

    def test_automatic_name_removed_before_mixed_script_check(self):
        result = translate_message("मेरा CloudDesk खाता", "Hindi", "English", [], True, FakeBackend())
        self.assertIn("CloudDesk", result.protected_terms)

    def test_repeated_terms_and_overlap(self):
        text = "FlyRank Pro and FlyRank; FlyRank Pro shows E403."
        masked, mapping = protect(text, ["FlyRank Pro", "FlyRank", "E403"])
        self.assertEqual(len(mapping), 4)
        self.assertEqual(restore(masked, mapping), text)

    def test_terms_do_not_replace_inside_other_words(self):
        masked, mapping = protect("cat category", ["cat"])
        self.assertIn("category", masked)
        self.assertEqual(len(mapping), 1)

    def test_dropped_and_duplicated_markers_rejected(self):
        masked, mapping = protect("FlyRank", ["FlyRank"])
        for output in ["missing", masked + masked]:
            with self.assertRaises(TranslationError):
                restore(output, mapping)

    def test_code_only_bypasses_model_and_detection(self):
        backend = FakeBackend()
        with patch("engine.detect_source", side_effect=AssertionError("must not detect")):
            result = translate_message("E403!", "Auto-detect", "Tamil", [], True, backend)
        self.assertEqual(result.translation, "E403!")
        self.assertEqual(result.status, "Preserved")
        self.assertEqual(backend.calls, [])

    def test_mixed_scripts_rejected_before_same_language_return(self):
        with self.assertRaisesRegex(TranslationError, "mixes scripts"):
            translate_message("मेरा account नहीं खुलता", "English", "English", [], True, FakeBackend())

    def test_manual_source_enables_short_message(self):
        backend = FakeBackend(lambda s: "Aidez-moi !")
        result = translate_message("Help!", "English", "French", [], True, backend)
        self.assertEqual(result.translation, "Aidez-moi !")
        with self.assertRaisesRegex(TranslationError, "too short"):
            translate_message("Help!", "Auto-detect", "French", [], True, backend)

    def test_sentence_mode_and_detection_only_once(self):
        backend = FakeBackend()
        with patch("engine.detect_source", return_value=("English", .99)) as detect:
            result = translate_message("This is urgent! Please help immediately!", "Auto-detect", "French", [], True, backend)
            self.assertEqual(detect.call_count, 1)
        self.assertEqual(result.sentence_count, 2)
        self.assertEqual(len(backend.calls[0][0]), 2)

    def test_protected_latin_name_not_mixed_script(self):
        result = translate_message("मेरा FlyRank खाता", "Hindi", "English", ["FlyRank"], True, FakeBackend())
        self.assertIn("FlyRank", result.translation)

    def test_invalid_empty_and_oversized_input(self):
        for text in ["", " " * 3, "a" * 4001]:
            with self.assertRaises(TranslationError):
                translate_message(text, "English", "French", [], True, FakeBackend())

    def test_foreign_sentence_marker_rejected(self):
        backend = FakeBackend(lambda s: s + " ZXQTERM999QXZ")
        with self.assertRaises(TranslationError):
            translate_message("FlyRank failed.", "English", "French", ["FlyRank"], True, backend)

    def test_same_language_explicit_status(self):
        backend = FakeBackend()
        result = translate_message("Hello there.", "English", "English", [], True, backend)
        self.assertEqual(result.status, "Unchanged")
        self.assertEqual(backend.calls, [])


if __name__ == "__main__":
    unittest.main()
