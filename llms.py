from anthropic import Anthropic
from anthropic.types import Message
import tiktoken
import copy
from openai import OpenAI
import os
class MixtralModel:
    def __init__(self, prompt, model="mistralai/Mixtral-8x7B-Instruct-v0.1") -> None:
        self.sys_prompt = prompt
        self.variant = model
        self.key = os.environ.get("MIXTRAL_KEY")
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=self.key,
            base_url='https://api.together.xyz',
        )
        self.variant = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    def get_completion(self, prompt, sys="", history= None):
        if history is None:
            if not sys.strip():
                chat_completion = self.client.chat.completions.create(messages=[{"role":"system","content":sys},{"role": "user","content": prompt,}],model=self.variant)
            else:
                chat_completion = self.client.chat.completions.create(messages=[{"role": "user","content": prompt,}],model=self.variant,max_tokens=4096)
        else:
            hst = ""
            hst = copy.deepcopy(history.copy())
            hst.append({"role":"user","content":prompt})
            chat_completion = self.client.chat.completions.create(messages=hst,model=self.variant)
        usage  = chat_completion.usage
        print(usage)
        return chat_completion.choices[0].message.content

class ClaudeModel:
    def __init__(self) -> None:
        self.client = Anthropic(api_key=os.environ.get("CLAUDE_KEY"))
        self.variant = "claude-3-sonnet-20240229"
    
    def predict(self, inp, hist=None) -> Message:
        if hist is None:
            message = self.client.messages.create(
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": inp,
                    }
                ],
                model=self.variant,
            )
            cost = (message.usage.input_tokens / 1_000_000) * 10
            cost += (message.usage.output_tokens / 1_000_000) * 20
            return message, cost
        else:
            history = hist
            history.append({
                        "role": "user",
                        "content": inp,
                    })
            message = self.client.messages.create(
                max_tokens=1024,
                messages=hist,
                model=self.variant,
            )
            cost = (message.usage.input_tokens / 1_000_000) * 10
            cost += (message.usage.output_tokens / 1_000_000) * 20
            return message, cost

