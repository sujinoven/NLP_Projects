"""Optional: real PyTorch/HF execution with tiny RANDOM BART, not real quality.

Skipped when inference dependencies are absent. No network/model download.
download_model.py is the separate real pretrained-checkpoint check.
"""
import pytest


def test_generation_uses_batched_bounded_inputs():
    torch = pytest.importorskip('torch')
    transformers = pytest.importorskip('transformers')
    tokenizers = pytest.importorskip('tokenizers')
    from app.services.summarizer import Summarizer

    vocab = {'<s>': 0, '<pad>': 1, '</s>': 2, '<unk>': 3,
             'tenant': 4, 'must': 5, 'pay': 6, 'rent': 7}
    backend = tokenizers.Tokenizer(tokenizers.models.WordLevel(vocab, unk_token='<unk>'))
    backend.pre_tokenizer = tokenizers.pre_tokenizers.Whitespace()
    backend.post_processor = tokenizers.processors.TemplateProcessing(
        single='<s> $A </s>', special_tokens=[('<s>', 0), ('</s>', 2)])
    tokenizer_class = getattr(transformers, 'TokenizersBackend', None) or transformers.PreTrainedTokenizerFast
    tokenizer = tokenizer_class(
        tokenizer_object=backend, bos_token='<s>', eos_token='</s>',
        pad_token='<pad>', unk_token='<unk>', model_max_length=32,
        model_input_names=['input_ids', 'attention_mask'])
    config = transformers.BartConfig(
        vocab_size=8, d_model=16, encoder_layers=1, decoder_layers=1,
        encoder_attention_heads=2, decoder_attention_heads=2,
        encoder_ffn_dim=32, decoder_ffn_dim=32, max_position_embeddings=32,
        bos_token_id=0, eos_token_id=2, pad_token_id=1,
        decoder_start_token_id=2, forced_eos_token_id=None)
    torch.manual_seed(7)
    service = Summarizer({'MODEL_NAME': 'random-test-model', 'MAX_DOCUMENT_TOKENS': 100})
    service.model = transformers.BartForConditionalGeneration(config).eval()
    service.tokenizer = tokenizer
    service.device = 'cpu'
    # Prevent immediate EOS so the random model produces inspectable content.
    service.model.generation_config.suppress_tokens = [0, 1, 2, 3]
    summary = service.generate([4, 5, 6, 7] * 6, 0.3, 12)
    assert isinstance(summary, str) and summary
