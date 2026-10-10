"""Lazy model loading keeps the setup screen available before model import."""
import json
import threading
from pathlib import Path
from preprocessing import clean_article
from model_compat import load_compatible_model

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / 'models'
LOCK = threading.Lock()
_loaded = None


def status():
    required = ['best_gru.keras', 'tokenizer.json', 'config.json']
    missing = [name for name in required if not (MODEL_DIR / name).is_file()]
    return {'ready': not missing, 'missing': missing, 'model': 'GRU'}


def load():
    global _loaded
    if _loaded is not None:
        return _loaded
    if not status()['ready']:
        raise ValueError('Import your Colab bundle first. See the setup instructions below.')
    import tensorflow as tf
    from tensorflow.keras.preprocessing.text import tokenizer_from_json
    cfg = json.loads((MODEL_DIR / 'config.json').read_text(encoding='utf-8'))
    if cfg.get('padding') != 'post' or cfg.get('truncating') != 'pre':
        raise ValueError('This app requires the right-padded GRU bundle from the Colab workflow.')
    length = cfg.get('sequence_length')
    if type(length) is not int or not 1 <= length <= 1024:
        raise ValueError('Invalid sequence length in config.json.')
    tokenizer = tokenizer_from_json((MODEL_DIR / 'tokenizer.json').read_text(encoding='utf-8'))
    model = load_compatible_model(MODEL_DIR / 'best_gru.keras', tf.keras.models.load_model)
    if model.input_shape[-1] != length or model.output_shape[-1] != cfg.get('vocab_size'):
        raise ValueError('Model dimensions do not match config.json. Re-export the same training run.')
    _loaded = model, tokenizer, cfg, tf.__version__
    return _loaded


def generate(text, count):
    if not isinstance(text, str) or not text.strip() or len(text) > 3000:
        raise ValueError('Enter between 1 and 3,000 characters.')
    if type(count) is not int or not 1 <= count <= 50:
        raise ValueError('Choose between 1 and 50 new words.')
    with LOCK:
        import numpy as np
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        model, tokenizer, cfg, runtime_version = load()
        cleaned = clean_article(text)
        ids = tokenizer.texts_to_sequences([cleaned])[0]
        if not ids:
            raise ValueError('Enter a phrase containing words or numbers.')
        oov = tokenizer.word_index.get(tokenizer.oov_token)
        initial_context = ids[-cfg['sequence_length']:]
        warnings = []
        unknown = sum(i == oov for i in initial_context)
        if unknown:
            warnings.append(f'{unknown} word(s) in the input context are outside the usable vocabulary.')
        if cfg.get('tensorflow_version') != runtime_version:
            warnings.append('The local TensorFlow version differs from the training version. Model loaded successfully; small numerical differences are possible.')
        valid = np.array([i for i in range(1, model.output_shape[-1])
                          if i != oov and i in tokenizer.index_word], dtype=np.int32)
        if not len(valid):
            raise ValueError('Tokenizer has no usable output words.')
        steps, suggestions = [], []
        for step in range(count):
            x = pad_sequences([ids], maxlen=cfg['sequence_length'], padding='post', truncating='pre', dtype='int32')
            probs = np.asarray(model(x, training=False))[0]
            if not np.all(np.isfinite(probs)):
                raise ValueError('The model returned invalid probabilities.')
            ranked = valid[np.argsort(probs[valid])[::-1][:5]]
            if step == 0:
                suggestions = [{'word': tokenizer.index_word[int(i)], 'probability': float(probs[i])} for i in ranked]
            best = int(ranked[0])
            word = tokenizer.index_word[best]
            steps.append({'step': step + 1, 'word': word, 'probability': float(probs[best])})
            # Re-tokenise the growing text exactly as the Colab generation function does.
            cleaned += ' ' + word
            ids = tokenizer.texts_to_sequences([cleaned])[0]
        return {'text': cleaned, 'steps': steps, 'suggestions': suggestions, 'warnings': warnings}
