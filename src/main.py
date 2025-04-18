import re
import sys
import requests
import os

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def build_prompt(fileContent):
    return f"""
Reestruture o conteúdo a seguir para que atenda aos requisitos de uma base de conhecimento clara, objetiva e adequada ao processamento por modelos de linguagem (LLMs) em tarefas de recuperação de informações via RAG (Retrieval-Augmented Generation).

Responda em pt-BR (português do Brasil).

Organize o conteúdo em seções hierárquicas, elimine elementos irrelevantes para leitura automatizada (como links, comentários e formatações decorativas) e priorize a clareza, a padronização terminológica e a consistência estrutural.

O objetivo é maximizar a eficiência na extração e compreensão de informações por LLMs.

Preserve todos os detalhes técnicos relevantes. Retorne exclusivamente o conteúdo reestruturado, sem quaisquer comentários adicionais.

{fileContent}
"""

def chat_with_model(token, prompt, model, temperature):
    url = 'http://localhost:3000/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": model,
      "temperature": temperature,
      "messages": [
        {
          "role": "user",
          "content": prompt
        }
      ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def save_result_to_file(file_name, content):
  os.makedirs(os.path.dirname(file_name), exist_ok=True)
  with open(file_name, 'w') as file:
    file.write(content)

if __name__ == "__main__":
    MIN_LINES_OF_CONTENT = 15
    MODEL = 'deepseek-r1:8b'
    TEMPERATURE = 0.1

    token = sys.argv[1]
    docs_path = sys.argv[2]

    print(f">> Running model \"{MODEL}\" on path \"{docs_path}\" with temperature \"{TEMPERATURE}\"")

    for root, dirs, files in os.walk(docs_path):
      for file in files:
        file_path = os.path.join(root, file)
        if not file.endswith('.md'):
            print(f"[!!!] Skipping file {file_path} as it is not a Markdown file.")
            continue
        file = open_file(file_path)
        if file.splitlines().__len__() < MIN_LINES_OF_CONTENT:
            print(f"[!!!] Skipping file {file_path} as it has less than {MIN_LINES_OF_CONTENT} lines.")
            continue
        print(f"""
=============================================
>>> Input: {file_path}""")
        prompt = build_prompt(file)
        response = chat_with_model(token, prompt, MODEL, TEMPERATURE)
        content = response['choices'][0]['message']['content']

        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        if 'error' in response:
            print(f"Error processing file {file_path}: {response['error']}")
            continue
        new_file_name = file_path.split('rd-documentation/pages/')[1].replace('/', '-').replace('default.md', '') + '.md'
        output_file_name = f'./output/{new_file_name}'
        save_result_to_file(output_file_name, content)
        print(f"""<<< Output: {output_file_name}
=============================================""")
