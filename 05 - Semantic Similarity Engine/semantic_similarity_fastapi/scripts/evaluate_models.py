from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.search_service import search_service  # noqa: E402


EVALUATION_QUERIES = [
    ("I forgot my password and cannot login", "Authentication"),
    ("I want to change my account details", "Account Management"),
    ("My payment did not go through", "Payments"),
    ("Where is my order", "Orders"),
    ("When will my package arrive", "Shipping"),
    ("I want my money back", "Refunds"),
    ("My subscription has expired", "Subscriptions"),
    ("The mobile app is not working", "Mobile App"),
    ("I am not receiving notifications", "Notifications"),
    ("I think my account has been hacked", "Security"),
    ("The website is not loading", "Website"),
    ("I need help from customer service", "Customer Support"),
]


OOV_QUERIES = [
    ("I forgot my passwrd and cannot loginn", "Authentication"),
    ("My paymnt did not go through", "Payments"),
    ("Where is my ordar", "Orders"),
    ("When will my pakage arrive", "Shipping"),
    ("I want a refnd for my purchase", "Refunds"),
    ("My subscriptin has expired", "Subscriptions"),
    ("The moblie app is not working", "Mobile App"),
    ("I am not receiving notificatons", "Notifications"),
    ("I think my acount has been hacked", "Security"),
    ("The websit is not loading", "Website"),
]


def precision_at_k(results: list[dict], expected_category: str, k: int) -> float:
    relevant = sum(
        row["category"] == expected_category
        for row in results[:k]
    )
    return relevant / k


def evaluate(test_set, k=5) -> pd.DataFrame:
    rows = []

    for query, expected_category in test_set:
        row = {
            "Query": query,
            "Expected Category": expected_category,
        }

        for model in ("tfidf", "word2vec", "fasttext"):
            response = search_service.search(query, model, k)
            row[model] = precision_at_k(
                response["results"],
                expected_category,
                k,
            )

        rows.append(row)

    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, label: str) -> None:
    print(f"\n{label}")
    print("=" * len(label))
    print(df.to_string(index=False))

    print("\nAverage Precision@5")
    print("-" * 30)

    for model in ("tfidf", "word2vec", "fasttext"):
        print(f"{model:10s}: {df[model].mean():.4f}")


if __name__ == "__main__":
    clean_df = evaluate(EVALUATION_QUERIES)
    oov_df = evaluate(OOV_QUERIES)

    summarize(clean_df, "Clean-query evaluation")
    summarize(oov_df, "OOV / misspelling evaluation")
