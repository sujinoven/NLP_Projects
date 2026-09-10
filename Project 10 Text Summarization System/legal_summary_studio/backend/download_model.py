"""Download/load and run one real summary before starting the UI."""
from app import create_app

if __name__ == "__main__":
    app = create_app()
    sample = ("Acme Corporation shall pay Globex Limited $50,000 by 1 July 2026. "
              "Late payments incur interest at 2% per month. Either party may terminate "
              "the agreement with thirty days of written notice. The obligation to pay "
              "outstanding invoices survives termination.")
    result = app.extensions["summarizer"].summarize(sample)
    print("REAL MODEL SUMMARY:", result["summary"])
    print("FACT MATCH REPORT:", result["facts"])
    print("Inspect the summary manually; successful generation does not prove accuracy.")
