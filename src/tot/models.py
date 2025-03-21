import os
import openai
import backoff

# from run_federated_test import federated_token_usage

completion_tokens = prompt_tokens = 0
slm_completion_tokens = slm_prompt_tokens = 0
llm_completion_tokens = llm_prompt_tokens = 0

api_base = "http://127.0.0.1:11451/v1"
api_key = "lm-studio"
# api_key = os.getenv("OPENAI_API_KEY", "")
if api_key != "":
    openai.api_key = api_key
else:
    print("Warning: OPENAI_API_KEY is not set")

# api_base = os.getenv("OPENAI_API_BASE", "")
openai.api_base = "http://127.0.0.1:11451/v1"
openai.api_key = "lm-studio"
if api_base != "":
    print("Warning: OPENAI_API_BASE is set to {}".format(api_base))
    openai.api_base = api_base


@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def gpt(
    args,
    prompt,
    model="gpt-4",
    temperature=0.9,
    max_tokens=1000,
    n=1,
    stop=None,
    api_base=openai.api_base,
    api_key=openai.api_key,
) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(
        args,
        messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        api_base=api_base,
        api_key=api_key,
    )


def chatgpt(
    args,
    messages,
    model="gpt-4",
    temperature=0.5,
    max_tokens=1000,
    n=1,
    stop=None,
    api_base=openai.api_base,
    api_key=openai.api_key,
) -> list:
    global completion_tokens, prompt_tokens, slm_completion_tokens, slm_prompt_tokens, llm_completion_tokens, llm_prompt_tokens
    from run_federated_test import federated_token_usage

    outputs = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = completions_with_backoff(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=cnt,
            stop=stop,
            api_base=api_base,
            api_key=api_key,
        )
        outputs.extend([choice["message"]["content"] for choice in res["choices"]])
        # log completion tokens
        completion_tokens += res["usage"]["completion_tokens"]
        prompt_tokens += res["usage"]["prompt_tokens"]
        if model == args.remotebackend:
            llm_completion_tokens += res["usage"]["completion_tokens"]
            llm_prompt_tokens += res["usage"]["prompt_tokens"]
        elif model == args.localbackend:
            slm_completion_tokens += res["usage"]["completion_tokens"]
            slm_prompt_tokens += res["usage"]["prompt_tokens"]
        elif model in federated_token_usage.keys():
            federated_token_usage[model]["completion_tokens"] += res["usage"]["completion_tokens"]
            federated_token_usage[model]["prompt_tokens"] += res["usage"]["prompt_tokens"]

    return outputs


def gpt_usage(backend="gpt-4o"):
    global completion_tokens, prompt_tokens, slm_completion_tokens, slm_prompt_tokens, llm_completion_tokens, llm_prompt_tokens
    cost = (
        llm_completion_tokens * 10 / 1000000 + llm_prompt_tokens * 2.5 / 1000000
    )  # prompt token: ￥2.5 / 1M tokens, completion token: ￥10 / 1M tokens
    return {
        "llm_completion_tokens": llm_completion_tokens,
        "llm_prompt_tokens": llm_prompt_tokens,
        "slm_completion_tokens": slm_completion_tokens,
        "slm_prompt_tokens": slm_prompt_tokens,
        "cost": cost,
    }
