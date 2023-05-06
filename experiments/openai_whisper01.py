# import openai_whisper
import whisper

openai_api_key = "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"

with openai_whisper.setup(api_key=openai_api_key):
    prompt = "What is the capital of France?"
    response = openai_whisper.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=10,
        n=1,
        stop=None,
        temperature=0.5
    )
    answer = response.choices[0].text.strip()
    print(f"Answer: {answer}")

#%%

#%%
