# Validation record

Date: 10 September 2026. Platform: Windows.

## Completed checks

| Check | Result |
|---|---|
| Backend API, text processing, fact matching, ROUGE and orchestration tests | 36 passed |
| Real PyTorch/Transformers generation with a tiny randomly initialized BART | 1 passed |
| Full backend test suite | **37 passed** |
| Dart formatting | Completed |
| `flutter analyze` | **No issues found** |
| Flutter HTTP contract, result-widget and Material-surface regression tests | **5 passed** |
| `flutter build web --dart-define=API_BASE_URL=http://127.0.0.1:5001` | **Succeeded** |
| Flutter WebAssembly dry run performed by build | Succeeded |
| PowerShell launcher syntax | Passed |
| ZIP CRC and required-file checks | Performed by scripts/package.py |

The web build emitted a missing optional Cupertino font warning; the custom UI uses Material icons. The build completed successfully. Browser inspection during the startup-screen fix confirmed that the page renders and that the new loading message is displayed during initialization. Full pretrained generation through the browser remains unverified.

## Startup-screen fix

The development page initially took about 20 seconds to initialize. Added a visible HTML startup message and initialization-error message using Flutter's bootstrap callbacks. Replaced a painted Container with a Material surface so ExpansionTile/ListTile content does not trigger the Flutter debug assertion about hidden ink/backgrounds. A regression test opens an expansion tile inside the card and checks for framework exceptions.

## Verified environment

- Python 3.12.14
- Flask 3.1.3; Flask-CORS 6.0.5
- PyTorch 2.14.0; Transformers 5.17.0; tokenizers 0.23.2
- rouge-score 0.1.2; pytest 9.1.1
- Flutter 3.47.3; Dart 3.13.3
- Flutter http package 1.6.0

Exact resolved Python inference dependencies are in `backend/requirements-lock.txt`. Flutter dependency versions are in `frontend/pubspec.lock`. SDK binaries and caches are not shipped.

## What these results do NOT establish

The full `facebook/bart-large-cnn` checkpoint was not downloaded or run during packaging. The integration test uses a small random model to exercise tensor construction and the actual generation API; it does not test summarization quality, the full checkpoint's download/loading, memory needs or timing.

Run `backend/download_model.py` after installing the locked dependencies, then test the sample through the live Flask API and Flutter UI. Those are separate real-checkpoint and end-to-end checks. The README provides exact commands.

There is no corpus ROUGE benchmark or legal-domain fine-tuning in this package. User-supplied reference scores apply only to that document/reference pair. No precision score in the UI certifies legal accuracy. Manually inspect amounts, parties, deadlines, roles, negations, exceptions and omissions.

## Meaningful regression coverage

- Every token remains covered in overlapping windows, including inputs with no sentence boundaries.
- Every chunk is bounded before model special tokens are added.
- Inline page references and negation survive cleanup.
- One-letter parties and changed dates/amounts are recognized by the supported patterns.
- `$50` does not incorrectly match `$500` or `$50,000`.
- No extracted items yields null match precision, rather than 100%.
- ROUGE matches a hand-calculated precision/recall/F1 example.
- Invalid JSON, missing input, invalid numeric settings, oversized documents and busy inference return appropriate errors.
- Model locks release after failures.
- Short documents are explicitly returned unchanged; long documents follow bounded reduction.
- Flutter passes the expected request fields and surfaces API errors.
