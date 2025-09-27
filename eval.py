import os
import ollama
import json
from datetime import datetime

with open("eval_prompts.json", "r") as f:
    evals = json.load(f)

#Two models
#models = ["llava-llama3:latest", "codellama:latest"]

#One model
models = ["llava-llama3:latest"]

# make results dir
os.makedirs("results", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = os.path.join("results", f"eval_results_{timestamp}.html")

html_header = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>LLM Eval Results</title>
<style>
  body{font-family:Segoe UI, Roboto, Arial; padding:20px; line-height:1.5; background:#0f1720; color:#e6eef6;}
  .model{font-size:1.1rem; font-weight:700; margin-top:1.2rem; color:#f8f9fb;}
  .task{margin-top:.6rem; padding:.6rem; border-radius:8px; background:#0b1220;}
  .prompt{color:#7bd1ff; font-weight:600;}
  .output{background:#08101a; padding:8px; border-radius:6px; margin-top:6px; white-space:pre-wrap; font-family:Menlo, Consolas, monospace; color:#d7e8ff;}
  .meta{color:#98a0b0; font-size:.9rem;}
</style>
</head>
<body>
<h1>LLM Eval Results</h1>
<p class="meta">Generated: {ts}</p>
<hr/>
""".replace("{ts}", timestamp)

html_footer = """
</body>
</html>
"""

with open(outfile, "w") as out:
    out.write(html_header)
    for model in models:
        out.write(f'<div class="model">=== Evaluating {model} ===</div>\n')
        for test in evals:
            response = ollama.chat(model=model, messages=[{"role":"user","content":test["prompt"]}])
            output = response["message"]["content"]
            out.write('<div class="task">')
            out.write(f'<div class="meta">Task: {test.get("task","")}</div>')
            out.write(f'<div class="prompt">Prompt: {test["prompt"]}</div>')
            out.write(f'<div class="output">{output}</div>')
            out.write('</div>\n')
    out.write(html_footer)

print(f"✅ HTML results saved to {outfile}")
