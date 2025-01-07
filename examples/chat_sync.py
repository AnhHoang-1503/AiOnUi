from aionui import AiOnUi

aionui = AiOnUi(config_path="config.yaml")

with aionui.model_sync("gpt") as model:
    model.chat("Hello, world!")
