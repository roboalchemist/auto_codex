from auto_codex.core import CodexRun, CodexSession

# Create and execute a single Codex run
run = CodexRun(
    prompt="Create a Python function to calculate fibonacci numbers",
    model="llama3",
    provider="ollama",
    timeout=300
)

result = run.execute(log_dir="./logs")
print(f"Success: {result.success}")
print(f"Files modified: {result.files_modified}") 