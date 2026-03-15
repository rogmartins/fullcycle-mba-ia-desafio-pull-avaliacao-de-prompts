"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
import yaml

load_dotenv()


def pull_prompts_from_langsmith(output_path: str):
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = os.getenv("PROMPT_NAME")
    prompt_identifier = f"{username}/{prompt_name}"

    print(f"Buscando prompt: {prompt_identifier}...")
    prompt = hub.pull(prompt_identifier)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    save_yaml(prompt, output_path)
    print(f"✅ Prompt salvo em YAML: {output_path}")
   

def main():
    """Função principal"""
    output_path = "prompts/raw_prompts.yml"
    pull_prompts_from_langsmith(output_path)


if __name__ == "__main__":
    sys.exit(main())
