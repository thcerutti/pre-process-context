import sys
import requests
import os
import uuid

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def build_prompt(fileContent):
    return f"""
    Reestruture o conteúdo abaixo para que ele sirva como base de conhecimento clara e objetiva, adequada para ser processada por uma LLM em tarefas de recuperação de contexto (RAG).

    Responda em pt-BR (português do Brasil).

    Organize o texto em seções hierárquicas, remova elementos irrelevantes para machine reading (como links e formatação decorativa) e priorize clareza, consistência e padronização de termos.

    O objetivo é facilitar a compreensão e extração de informações por LLMs.

    Mantenha detalheas técnicos importantes. Retorne somente o texto estruturado, sem comentários adicionais.

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
    token = sys.argv[1]
    docs_path = sys.argv[2]
    model = 'codellama:latest'
    temperature = 0.2
    print(f">> Running model \"{model}\" on path \"{docs_path}\" with temperature \"{temperature}\"")

    for root, dirs, files in os.walk(docs_path):
      for file in files:
        file_path = os.path.join(root, file)
        if not file.endswith('.md'):
            continue
        print(f"""
=============================================
Processing file: {file_path}
=============================================
""")
        prompt = build_prompt(open_file(file_path))
        response = chat_with_model(token, prompt, model, temperature)
        content = response['choices'][0]['message']['content']
        if 'error' in response:
            print(f"Error processing file {file_path}: {response['error']}")
            continue
        new_file_name = file_path.split('rd-documentation/pages/')[1].replace('/', '-').replace('default.md', '') + '.md'
        save_result_to_file(f'./output/{new_file_name}', content)
