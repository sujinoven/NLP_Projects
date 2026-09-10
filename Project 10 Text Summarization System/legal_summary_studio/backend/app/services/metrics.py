"""ROUGE uses a user-supplied reference, never the full source as a substitute."""
from rouge_score.rouge_scorer import RougeScorer


def rouge_report(reference, prediction):
    scores = RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True).score(reference, prediction)
    return {key: {"precision": value.precision, "recall": value.recall,
                  "f1": value.fmeasure} for key, value in scores.items()}
