# Customer Feedback Analysis System - Main WebApp Entry Point
import sys
import socket
import uvicorn

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    port = 8000
    if is_port_in_use(port):
        port = 8050
        
    print("\n" + "="*70)
    print("Starting FeedbackPulse AI - Customer Feedback Sentiment Analyzer WebApp")
    print("Telegram Bot: @Feedback_Analyser_bot")
    print(f"Web Application URL: http://127.0.0.1:{port}")
    print(f"API Documentation:   http://127.0.0.1:{port}/docs")
    print("="*70 + "\n")

    uvicorn.run("src.api.app:app", host="127.0.0.1", port=port, reload=False)