import pytest
from app import create_app
from app.services.summarizer import ServiceError


class FakeService:
    def __init__(self):
        self.calls = []

    def health(self):
        return {'status': 'ok', 'model_state': 'test-double'}

    def summarize(self, *args):
        self.calls.append(args)
        return {'summary': 'Test summary'}


@pytest.fixture
def fixture():
    service = FakeService()
    app = create_app({'TESTING': True}, service=service)
    return app.test_client(), service


def test_health_does_not_run_inference(fixture):
    client, service = fixture
    assert client.get('/api/health').status_code == 200
    assert service.calls == []


@pytest.mark.parametrize('payload', [[], {}, {'text': ''}, {'text': 3},
    {'text': 'ok', 'target_ratio': True}, {'text': 'ok', 'target_ratio': 0.9},
    {'text': 'ok', 'target_ratio': float('nan')},
    {'text': 'ok', 'max_summary_tokens': 220.5},
    {'text': 'ok', 'max_summary_tokens': True},
    {'text': 'ok', 'reference': []}])
def test_invalid_requests_do_not_call_model(fixture, payload):
    client, service = fixture
    assert client.post('/api/summarize', json=payload).status_code == 400
    assert not service.calls


def test_reference_and_parameters_forwarded(fixture):
    client, service = fixture
    response = client.post('/api/summarize', json={
        'text': 'Some legal text', 'target_ratio': 0.4,
        'max_summary_tokens': 120, 'reference': ' Reference '})
    assert response.status_code == 200
    assert service.calls == [('Some legal text', 0.4, 120, 'Reference')]


def test_oversize_document(fixture):
    client, service = fixture
    assert client.post('/api/summarize', json={'text': 'a' * 60001}).status_code == 413
    assert not service.calls


def test_json_http_errors(fixture):
    client, _ = fixture
    assert 'error' in client.get('/missing').get_json()
    assert client.post('/api/summarize', data='{broken', content_type='application/json').status_code == 400


def test_busy_model_error(fixture):
    client, service = fixture
    def busy(*args):
        raise ServiceError('Busy', 429)
    service.summarize = busy
    response = client.post('/api/summarize', json={'text': 'Document'})
    assert response.status_code == 429
    assert response.get_json() == {'error': 'Busy'}


def test_cors_restricts_origins(fixture):
    client, _ = fixture
    good = client.get('/api/health', headers={'Origin': 'http://localhost:5173'})
    bad = client.get('/api/health', headers={'Origin': 'http://unlisted.example'})
    assert good.headers['Access-Control-Allow-Origin'] == 'http://localhost:5173'
    assert 'Access-Control-Allow-Origin' not in bad.headers
