from aionui import AiOnUi
import asyncio

aionui = AiOnUi()


def sync_example():
    with aionui.model_sync("gpt") as model:
        response = model.chat("Hello, how are you?")
        print("GPT Response:", response)

        code_response = model.chat("Write a function to calculate the sum of two numbers", expected_result="code")
        print("Code Response:", code_response)

        model.text_as_file("Content that needs to be analyzed, something very long...", "data.txt")

    with aionui.model_sync("claude") as model:
        response = model.chat("Analyze the following text: Hello World!")
        print("Claude Response:", response)

    with aionui.model_sync("gemini") as model:
        response = model.chat("Compare Python and JavaScript")
        print("Gemini Response:", response)


async def async_example():
    async with aionui.model_async("gpt") as model:
        response = await model.chat("Hello!")
        print("Async GPT Response:", response)

        response = await model.chat("What's the latest news about AI?", tools=["search_the_web"])
        print("Web Search Response:", response)

    async with aionui.model_async("claude") as model:
        await model.text_as_file("Content that needs to be analyzed, something very long...", "data.txt")
        response = await model.chat("Analyze the uploaded data")
        print("File Analysis Response:", response)

    async with aionui.model_async("gemini") as model:
        json_response = await model.chat("List 3 programming languages and their features", expected_result="json")
        print("JSON Response:", json_response)


if __name__ == "__main__":
    print("Running sync examples...")
    sync_example()

    print("\nRunning async examples...")
    asyncio.run(async_example())
