import re
import sys
import requests
import os

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def build_prompt(fileContent):
    return f"""
Reestruture o conteúdo a seguir para que ele seja adequado ao uso como base de conhecimento em sistemas de recuperação aumentada por geração (RAG – Retrieval-Augmented Generation), com foco em máxima eficiência na extração de informações por modelos de linguagem (LLMs).

Responda em pt-BR (português do Brasil).

## Objetivos:
Tornar o conteúdo mais acessível e preciso para respostas automáticas baseadas em contexto.

Permitir que partes isoladas do texto contenham informações completas e autossuficientes, sem depender de outras seções para fazer sentido.

## Instruções:

- Reorganize o conteúdo com títulos claros e hierárquicos, utilizando seções e subseções que representem os conceitos descritos.

- Explique todos os termos técnicos com clareza e contexto, mesmo que isso repita parte da explicação em seções diferentes.

- Use bullets, listas numeradas e enumerações sempre que houver agrupamentos de informações.

- Inclua sinônimos ou variações terminológicas relevantes próximos a cada conceito importante (ex: “Traces (rastros)” ou “Serviços (também chamados de ‘Services’)”).

- Torne todas as informações explícitas e autoexplicativas, evitando dependência de links, imagens ou contexto externo.

- Remova elementos desnecessários para leitura automatizada, como comentários, links não informativos, formatação visual (linhas decorativas, divisores, etc).

- Priorize clareza, consistência e padronização do vocabulário técnico ao longo de todo o conteúdo.

- Elimine introduções vagas ou frases genéricas que não agreguem à recuperação da informação.

Importante: Se alguma informação estiver ausente ou se não houver dados suficientes para responder a uma pergunta de forma precisa, isso deve ser declarado explicitamente. Não faça suposições ou inferências além do conteúdo fornecido.

## Saída esperada:

Apenas o conteúdo reestruturado, organizado e limpo, pronto para ser indexado em um sistema de RAG.

{fileContent}
"""

def chat_with_model(token, prompt, model, temperature, top_p):
    url = 'http://localhost:3000/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": model,
      "temperature": temperature,
      "top_p": top_p,
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

def get_files_in_directory(directory):
    MIN_LINES_OF_CONTENT = 15
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            file_path = os.path.join(root, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) < MIN_LINES_OF_CONTENT:
                    continue
            if os.path.isfile(file_path):
                files.append(file_path)
    return files

if __name__ == "__main__":
    MODEL = 'deepseek-r1:8b'
    TEMPERATURE = 0.1
    TOP_P = 0.1

    token = sys.argv[1]
    docs_path = sys.argv[2]

    print(f">> Running model \"{MODEL}\" on path \"{docs_path}\" with temperature \"{TEMPERATURE}\"")

    files_to_process = get_files_in_directory(docs_path)
    if not files_to_process:
        print(f"[!!!] No files found in the directory {docs_path}.")
        sys.exit(1)
    total_files = len(files_to_process)
    print(f"[INFO] Found {total_files} files in the directory {docs_path}.")
    files_processed = 0

    for file_path in files_to_process:
        print(f">>> [INPUT] {file_path}")
        file_content = open_file(file_path)
        prompt = build_prompt(file_content)
        response = chat_with_model(token, prompt, MODEL, TEMPERATURE, TOP_P)
        content = response['choices'][0]['message']['content']

        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        if 'error' in response:
            print(f"Error processing file {file_path}: {response['error']}")
            continue
        new_file_name = file_path.split('rd-documentation/pages/')[1].replace('/', '-').replace('default.md', '') + '.md'
        output_file_name = f'./output/{new_file_name}'
        save_result_to_file(output_file_name, content)
        files_processed += 1
        percentage = (files_processed / total_files) * 100
        print(f"""<<< [OUTPUT]: {output_file_name}
[INFO] Processed {files_processed}/{total_files} files ({percentage:.2f}%)
=============================================""")
