#!/usr/bin/env python3

import os
import subprocess

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]

PROMPT = f"you are a coding agent at {os.getcwd()}, use bash to solve tasks, Act, don't explain."

TOOLS =[{
    "name":"bash",
    "description":"run a shell bash",
    "input_schema":{
         "type":"object",
         "properties":{"command":{"type":"string"}},
         "required": ["command"]
     }
}]

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot"]
    if any(d in command for d in dangerous):
        return "Error, Dangerous command block"
    try:
        result = subprocess.run(command, 
                                shell=True,
                                cwd=os.getcwd(),
                                capture_output=True,
                                text=True,
                                timeout=120)
        output = (result.stdout + result.stderr).strip()
        return output
    except subprocess.TimeoutExpired:
        return "Error: Timeout(120s)"

def agent_loop(messages: list):
    for iteration in range(1, 100):
        print(f"\033[35m[Iteration {iteration}]\033[0m")
        response = client.messages.create(model=MODEL,
                                          system=PROMPT,
                                          tools=TOOLS,
                                          messages=messages,
                                          max_tokens=8000
                                          )
        messages.append({"role": "assistant", "content": response.content})
        
        print(response.content)
        if response.stop_reason != "tool_use":
            return
        
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\033[33m$ {block.input["command"]}\033[0m")
                output = run_bash(block.input['command'])
                print(output[:200])
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
    