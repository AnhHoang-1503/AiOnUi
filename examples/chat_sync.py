from aionui import AiOnUi, AiModel, ExpectedResult

aionui = AiOnUi(config_path="config.yaml")

with aionui.model_sync(AiModel.GPT) as model:
    model.chat("Hello, world!")
