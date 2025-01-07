from aionui import AiOnUi

aionui = AiOnUi(config_path="config.yaml")


async def main():
    async with aionui.model_async("gpt") as model:
        model.chat("Hello, world!")

    async with aionui.model_async("claude") as model:
        model.chat("Hello, world!")

    async with aionui.model_async("gemini") as model:
        model.chat("Hello, world!")
