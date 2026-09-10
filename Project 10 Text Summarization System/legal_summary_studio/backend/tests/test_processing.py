import pytest
from app.services.text_processing import preprocess, token_windows
from app.services.facts import fact_report
from app.services.metrics import rouge_report


def test_cleanup_preserves_reference_and_paragraphs():
    text = 'Party A must NOT pay $50,000.\n\nSee Page 3 of 12.\nPage 2 of 8\nEnd.'
    cleaned = preprocess(text)
    assert 'See Page 3 of 12.' in cleaned
    assert 'Page 2 of 8' not in cleaned
    assert 'NOT pay $50,000.' in cleaned
    assert '\n\n' in cleaned


@pytest.mark.parametrize('length', [0, 1, 1022, 1023, 3000, 20000])
def test_windows_cover_every_token_without_overflow(length):
    ids = list(range(length))
    chunks = token_windows(ids)
    assert all(len(chunk) <= 1022 for chunk in chunks)
    assert {x for chunk in chunks for x in chunk} == set(ids)
    assert all(chunk == list(range(chunk[0], chunk[-1] + 1)) for chunk in chunks)
    if len(chunks) > 1:
        assert chunks[0][-64:] == chunks[1][:64]


def test_bad_overlap_rejected():
    with pytest.raises(ValueError):
        token_windows([1], capacity=5, overlap=5)


def test_empty_facts_are_not_perfect_accuracy():
    assert fact_report('ordinary words', 'brief words')['match_precision'] is None


def test_facts_detect_changed_party_amount_and_date():
    result = fact_report('Party A pays Party B $50,000 on 1 July 2026.',
                         'Party A pays Party C $60,000 on 1 August 2026.')
    assert {'Party C', '$60,000', '1 August 2026'} <= set(result['not_found_in_source'])


def test_fact_substrings_do_not_match():
    result = fact_report('Party AB pays $500.', 'Party A pays $50.')
    assert result['match_precision'] == 0


def test_partial_amount_with_separator_does_not_match():
    assert fact_report('The fee is $50,000.', 'The fee is $50.')['match_precision'] == 0


def test_rouge_known_example():
    result = rouge_report('tenant must pay rent monthly', 'tenant must pay rent')['rouge1']
    assert result['precision'] == 1
    assert result['recall'] == pytest.approx(0.8)
    assert result['f1'] == pytest.approx(8 / 9)
