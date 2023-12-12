# devrev-ai-agents

## Setup

- Use `pip install -r requirements.txt` for initial setup and dependency installation.

## Langchain Demo

- **Implementation:** Directory: `Langchain/`
- **How to run:**
  1. Update query in `LangchainDemo.py`
  2. Run `python LangchainDemo.py`

## PalmSeg Demo

- **Implementation:** Directory: `palm_subtask_responses/`
- **How to run:**
  1. Update query in `PalmSegDemo.py`
  2. Run `python PalmSegDemo.py`

## Memory Integration

- **Implementation:** Directory: `Memory/`

## Function Embeddings

- **Implementation:** Directory: `function_embeddings`
- Creating rich function description using arguments and example
- Calculating embedding and doing similarity search
- Storing function descriptions in vector database

## Adding a New Task

- Guidelines or instructions for adding a new task.

## Experiments description:

- Experiment_v0.py: We constructed a dataset and benchmarked our implementations of ReAct + Langchain.
- Experiment_v1.py: We constructed a dataset and benchmarked our implementations of PaLM + query segementation.

## Comparitive Analysis between Experiements
- Latency comparison
![latency comparison](/images/latency_comparison.png)
- token comparison
![token comparison](/images/token_comparison.png)

## How to Add/Search/get All tools?

using `add_new_tools.py` script:

1. Use `python3 add_new_tools.py --help` to view possible commands. Currently following commands are supported:

- getAllTools:
  - Arguments 1: `--model` : choices = {palm,openai}, optional, default= openai
  - Arguments 2: `--showDescription` : Add this flag to show description of tools, along with names, optional, default= False
  - Usage: `python3 add_new_tools.py getAllTools --model openai --showDescription`
- searchTools:
  - Arguments 1: `--model` : choices = {palm,openai}, optional, default= openai
  - Arguments 2: `--toolName` : Name of tool to search, required
  - Usage: `python3 add_new_tools.py searchTools --model openai --toolName "works_list"`
- addTool:
  - Arguments 1: `--model` : choices = {palm,openai}, optional, default= openai
  - Arguments 2: `--fileName` : JSON file path where tool description is stored, required
  - Usage: `python3 add_new_tools.py addTool --model openai --fileName "tools_description.json"`
