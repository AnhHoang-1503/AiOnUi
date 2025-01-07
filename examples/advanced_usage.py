from aionui import AiOnUi
import asyncio
import json


aionui = AiOnUi("config.yaml")


async def process_large_file():
    async with aionui.model_async("claude") as model:
        large_text = "Very large text content...\n" * 1000
        await model.text_as_file(large_text, "large_data.txt")

        questions = ["Summarize the key points", "Find all numerical data", "List main topics", "Identify patterns"]

        results = []
        for question in questions:
            response = await model.chat(f"Based on the uploaded file, {question}", expected_result="json")
            results.append(json.loads(response))

        return results


async def collaborative_analysis():
    text = "Complex text requiring multiple perspectives..."

    async with aionui.model_async("gpt") as gpt, aionui.model_async("claude") as claude, aionui.model_async(
        "gemini"
    ) as gemini:

        tasks = [
            gpt.chat("Analyze sentiment and tone: " + text),
            claude.chat("Identify key concepts and relationships: " + text),
            gemini.chat("Provide alternative viewpoints: " + text),
        ]

        results = await asyncio.gather(*tasks)
        return {"sentiment": results[0], "concepts": results[1], "viewpoints": results[2]}


async def code_generation_workflow():
    async with aionui.model_async("gpt") as gpt, aionui.model_async("claude") as reviewer:
        code = await gpt.chat("Write a Python class for a REST API client", expected_result="code")
        await reviewer.text_as_file(code, "code.py")
        review = await reviewer.chat(
            """Review the code for:
            1. Best practices
            2. Security issues
            3. Performance improvements
            4. Error handling
            Return in JSON format
            """,
            expected_result="json",
        )

        improved_code = await gpt.chat(f"Improve the code based on this review: {review}", expected_result="code")

        return {"original": code, "review": json.loads(review), "improved": improved_code}


async def main():
    print("Processing large file...")
    file_results = await process_large_file()
    print(json.dumps(file_results, indent=2))

    print("\nPerforming collaborative analysis...")
    analysis_results = await collaborative_analysis()
    print(json.dumps(analysis_results, indent=2))

    print("\nGenerating and reviewing code...")
    code_results = await code_generation_workflow()
    print(json.dumps(code_results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
