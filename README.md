# AI On UI (aionui)

[![PyPI version](https://badge.fury.io/py/aionui.svg)](https://badge.fury.io/py/aionui)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python library for automating interactions with AI models (ChatGPT, Claude, Gemini) through their web interfaces. Supports both synchronous and asynchronous operations, file handling, and cross-platform compatibility.

## Key Features

- 🤖 **Multiple AI Model Support:**
  - ChatGPT
  - Claude
  - Gemini

- 🔄 **Dual Operation Modes:**
  - Sync: for sequential code
  - Async: for asynchronous applications

- 📦 **Versatile Data Handling:**
  - Text responses
  - Code blocks
  - JSON structures
  - Images
  - File upload/download

- 🛠 **Advanced Features:**
  - Web search (ChatGPT)
  - Large file processing
  - Retry mechanism
  - Detailed logging
  - Cross-platform support

## Installation

```bash
pip install aionui
```

## Requirements

- Python 3.10+
- Google Chrome
- Playwright

## Quickstart

### Synchronous Usage

```python
from aionui import AiOnUi

# Initialize
aionui = AiOnUi()

# ChatGPT
with aionui.model_sync("gpt") as model:
    response = model.chat("Hello!")
    print(response)

# Claude
with aionui.model_sync("claude") as model:
    response = model.chat("Hello!")
    print(response)

# Gemini
with aionui.model_sync("gemini") as model:
    response = model.chat("Hello!")
    print(response)
```

### Asynchronous Usage

```python
import asyncio
from aionui import AiOnUi

async def main():
    aionui = AiOnUi()
    
    async with aionui.model_async("gpt") as model:
        response = await model.chat("Hello!")
        print(response)

# Run
asyncio.run(main())
```

## Configuration

Create a `config.yaml` file:

```yaml
# Chrome settings
chrome_binary_path: "/usr/bin/google-chrome"  # Path to Chrome binary
user_data_dir: "~/chrome-data"                # Profile directory
debug_port: 9222                              # Port to connect over devtools protocol
```

Use the config:

```python
aionui = AiOnUi("config.yaml")
```

## Advanced Examples

### File Upload and Analysis

```python
async with aionui.model_async("claude") as model:
    # Upload file
    await model.text_as_file("Content for analysis", "data.txt")
    
    # Analyze
    response = await model.chat("Analyze the uploaded data")
    print(response)
```

### Web Search with ChatGPT

```python
with aionui.model_sync("gpt") as model:
    response = model.chat(
        "Latest news about AI?",
        tools=["search_the_web"]
    )
    print(response)
```

### JSON Response

```python
with aionui.model_sync("gemini") as model:
    json_response = model.chat(
        "List 3 programming languages",
        expected_result="json"
    )
    print(json_response)
```

## Documentation

See more examples and detailed guides in the [examples](./examples) directory.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for more details.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Credits

Copyright (c) 2024 Vu Tri Anh Hoang - [GitHub](https://github.com/vutrianhhoang)