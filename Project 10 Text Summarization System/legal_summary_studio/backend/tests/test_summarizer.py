from types import SimpleNamespace
import pytest
from app.services.summarizer import Summarizer, ServiceError


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return list(text.encode('ascii'))

    def num_special_tokens_to_add(self, pair=False):
        return 2


class FakeSummarizer(Summarizer):
    """Only orchestration is tested; this does not validate model quality."""
    def load(self):
        self.tokenizer = FakeTokenizer()
        self.model = SimpleNamespace(config=SimpleNamespace(max_position_embeddings=1024))
        self.state = 'ready'

    def generate(self, ids, ratio, max_tokens):
        assert len(ids) <= 1022
        return bytes(ids[:max(2, min(max_tokens, int(len(ids) * ratio)))]).decode('ascii').strip()


def make_service():
    return FakeSummarizer({'MODEL_NAME': 'test-double', 'MAX_DOCUMENT_TOKENS': 20000})


def test_short_input_preserved_and_labeled():
    result = make_service().summarize('Payment is due.')
    assert result['summary'] == 'Payment is due.'
    assert result['passes'] == 0
    assert result['compression_ratio'] == 1
    assert any('unchanged' in warning for warning in result['warnings'])


def test_long_unpunctuated_document_reduces_without_overflow():
    result = make_service().summarize('abcdefghijklmnopqrstuvwxyz' * 200)
    assert result['chunks'] > 1
    assert result['passes'] >= 2
    assert result['summary_tokens'] < result['input_tokens']


def test_empty_after_cleanup_and_lock_release():
    service = make_service()
    with pytest.raises(ServiceError) as error:
        service.summarize('Page 2 of 3')
    assert error.value.status == 400
    assert not service.lock.locked()


def test_failed_generation_releases_lock():
    service = make_service()
    def fail(*args):
        raise RuntimeError('test failure')
    service.generate = fail
    with pytest.raises(RuntimeError):
        service.summarize('abcdefghijklmnopqrstuvwxyz' * 5)
    assert not service.lock.locked()


def test_busy_rejected_immediately():
    service = make_service()
    service.lock.acquire()
    try:
        with pytest.raises(ServiceError) as error:
            service.summarize('hello')
        assert error.value.status == 429
    finally:
        service.lock.release()


def test_token_limit():
    with pytest.raises(ServiceError) as error:
        make_service().summarize('x' * 20001)
    assert error.value.status == 413


def test_reference_enables_rouge_only_when_supplied():
    service = make_service()
    assert service.summarize('Payment is due.')['rouge'] is None
    assert service.summarize('Payment is due.', reference='Payment is due.')['rouge']['rouge1']['f1'] == 1
