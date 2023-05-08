# import openai_whisper
import whisper

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("Nie udało się odczytać wartości zmiennej środowiskowej OPENAI_API_KEY.")
    exit(1)

with openai_whisper.setup(api_key=api_key):
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
