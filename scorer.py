import os, json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("CLAUDE_KEY"))

SCORE_SCHEMA = {
  "name": "score_hook",
  "description": "Score a direct-response video ad hook.",
  "input_schema": {
    "type": "object",
    "properties": {
      "attention": {
        "type": "integer",
        "description": "1-5. Does it stop the scroll in the first 3 seconds?"
      },
      "clarity": {
        "type": "integer",
        "description": "1-5. Is the value proposition immediately legible?"
      },
      "specificity": {
        "type": "integer",
        "description": "1-5. Concrete claim vs. vague hype?"
      },
      "tension": {
        "type": "integer",
        "description": "1-5. Does it open a curiosity gap that demands resolution?"
      },
      "overall": {
        "type": "integer",
        "description": "1-5 overall."
      },
      "reasoning": {
        "type": "string",
        "description": "2-3 sentences"
      },
      "strongest_rewrite": {
        "type": "string",
        "description": "One improved version of the hook."
      },
    },
    "required": [
      "attention",
      "clarity",
      "specificity",
      "tension",
      "overall",
      "reasoning",
      "strongest_rewrite"
    ]
  },
}

SYSTEM = """You are a direct-response creative strategist evaluating video ad hooks for paid social.
A hook is the first 2-3 seconds. It MUST stop a person from scrolling past it.

Score against these criteria. Be harsh. Most hooks are lame and mediocre.

Examples of a 5 on attention: "I fired my accountant after I found this."
Examples of a 1 on attention: "Introducing our new product line."

Examples of a 5 on specificity: "This cut my grocery bill by $312 a month."
Examples of a 1 on specificity: "Save money on groceries with our amazing app."

Always call the score_hook tool. Never respond in plain prose."""

def score_hook(hook: str) -> dict:
  response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1000,
    system = SYSTEM,
    tools = [SCORE_SCHEMA],
    tool_choice = {
      "type": "tool",
      "name": "score_hook"
    },
    messages = [
      {
        "role": "user",
        "content": f"Score this hook:\n\n{hook}"
      }
    ]
  )
  for block in response.content:
    if block.type == "tool_use":
      return block.input
  raise ValueError("Model did not return structured output")

if __name__ == "__main__":
  result = score_hook("Introducing our new premium skincare collection.")
  print(json.dumps(result, indent=2))