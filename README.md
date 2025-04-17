# pre-process-context

This project automates the process of standardizing and restructuring technical documentation files to optimize their use as contextual data for Large Language Models (LLMs) in Retrieval-Augmented Generation (RAG) pipelines.

It scans a directory of documentation files, applies a customizable prompt to each one, and outputs cleaned, structured content designed to enhance information retrieval and accuracy in LLM-based systems.

The goal is to improve the quality and consistency of contextual data for better performance in local or hosted LLM environments such as OpenWebUI.


## Project Structure

```
my-python-project
├── src
│   └── main.py       # Contains the main logic of the application
├── requirements.txt   # Lists the dependencies required for the project
└── README.md          # Documentation for the project
```

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```
   git clone <repository-url>
   cd my-python-project
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python src/main.py
   ```

## Usage

The main function in `main.py` is `chat_with_model(token)`, which requires an API token for authorization. Modify the `token` variable in the script to use your own token.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
