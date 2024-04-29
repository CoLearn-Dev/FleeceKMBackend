export PATH="$HOME/.local/bin:$PATH"

 poetry run uvicorn fleecekmbackend.main:app --host 0.0.0.0 --port 12345