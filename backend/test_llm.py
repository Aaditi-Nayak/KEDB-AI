from app.ai.llm import generate_answer

answer = generate_answer(
    "Say hello in one sentence."
)

print(answer)