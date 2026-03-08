#!/usr/bin/env python3

import os
import subprocess

from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]
WORKDIR = Path.cwd()

SYSTEM = f"you are a coding agent at {os.getcwd()}, use bash to solve tasks, Act, don't explain."

def safe_path(raw_path: str) -> Path:
    resolve_path = (WORKDIR / raw_path).resolve()
    if not resolve_path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {raw_path}")
    return resolve_path
 
def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command block"
    try:
        result = subprocess.run(command, 
                                shell=True,
                                cwd=os.getcwd(),
                                capture_output=True,
                                text=True,
                                timeout=120)
        output = (result.stdout + result.stderr).strip()
        return output[:50000]
    except subprocess.TimeoutExpired:
        return "Error: Timeout(120s)"

def run_read(path: str, limit: int = None):
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"...({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error {e}"

def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error {e}"

TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "run_read": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "run_write": lambda **kw: run_write(kw["path"], kw["content"]),
    "run_edit": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
}
TOOLS =[{
    "name":"bash",
    "description":"run a shell bash",
    "input_schema":{
         "type":"object",
         "properties":{"command":{"type":"string"}},
         "required": ["command"]
        }
    },
    {
    "name":"run_read",
    "description":"Read file contents.",
    "input_schema":{
         "type":"object",
         "properties":{
                    "path":{"type":"string"},
                    "limit":{"type":"integer"}},
         "required": ["path"]
        }
    },
    {
    "name":"run_write",
    "description":"Write contents to file",
    "input_schema":{
         "type":"object",
         "properties":{
                    "path":{"type":"string"},
                    "content":{"type":"string"}},
         "required": ["path", "content"]
        }
    },
    {
    "name":"run_edit",
    "description":"Replace exact text in file",
    "input_schema":{
         "type":"object",
         "properties":{
                    "path":{"type":"string"},
                    "old_text":{"type":"string"},
                    "new_text":{"type":"string"}},
         "required": ["path", "old_text", "new_text"]
        }
    }
]

def agent_loop(messages: list):
    for iteration in range(1, 100):
        print(f"\033[35m[Iteration {iteration}]\033[0m")
        response = client.messages.create(model=MODEL,
                                          system=SYSTEM,
                                          tools=TOOLS,
                                          messages=messages,
                                          max_tokens=8000
                                          )
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason != "tool_use":
            return
        
        results = []
        for block in response.content:
            if hasattr(block, 'text') and block.text:
                print(f"\033[33m{block.text}\033[0m")
            if block.type == "tool_use":
                if block.name:
                    print(f"\033[36mTool: {block.name}\033[0m")
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                print(f"\033[32m{output[:200]}\033[0m")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                               "content": output})
        messages.append({"role": "user", "content": results})
        
if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms1>> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "quit", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for block in response_content:
                if hasattr(block, "text"):
                    print(block.text)
        print()
    