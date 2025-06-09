curl http://172.16.226.32:11434/api/generate -d '
{
  "model": "tinyllama",
  "prompt": "Why is the sky blue?",
  "stream": false,
  "options": {
    "num_thread": 8,
    "num_ctx": 2024
  }
}' | jq .



curl http://172.16.226.32:11434