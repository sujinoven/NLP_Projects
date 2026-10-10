"""Local API server; one process avoids loading duplicate model copies."""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    from waitress import serve
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5001"))
    print(f"Legal Summary API: http://{host}:{port}/api/health", flush=True)
    serve(app, host=host, port=port, threads=4)
