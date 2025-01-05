from aionui import AiOnUI, AiModel, ExpectedResult

with AiOnUI(AiModel.GPT, "config.yaml") as ai:
    response = ai.chat("Xin chào", ExpectedResult.Text)
    print(response)
