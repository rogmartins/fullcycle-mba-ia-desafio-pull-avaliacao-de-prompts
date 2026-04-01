"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v2"
PROMPTS_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        username = os.getenv("USERNAME_LANGSMITH_HUB")
        prompt_identifier = f"{username}/{prompt_name}"

        system_prompt = prompt_data.get("system_prompt", "").strip()
        user_prompt = prompt_data.get("user_prompt", "").strip()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        tags = prompt_data.get("tags", [])
        description = prompt_data.get("description", "")

        print(f"Fazendo push do prompt: {prompt_identifier}...")
        hub.push(
            prompt_identifier,
            prompt,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags if tags else None,
        )
        print(f"✅ Push realizado com sucesso: {prompt_identifier}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    if "system_prompt" not in prompt_data:
        errors.append("Campo obrigatório faltando: system_prompt")
    elif not prompt_data["system_prompt"].strip():
        errors.append("system_prompt está vazio")

    if "user_prompt" not in prompt_data:
        errors.append("Campo obrigatório faltando: user_prompt")
    elif not prompt_data["user_prompt"].strip():
        errors.append("user_prompt está vazio")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de Prompts para LangSmith Hub")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    print(f"Carregando prompts de: {PROMPTS_FILE}")
    data = load_yaml(str(PROMPTS_FILE))
    if not data:
        return 1

    # Extrai os dados do prompt da primeira chave do YAML
    prompt_key = list(data.keys())[0]
    prompt_data = data[prompt_key]

    print_section_header(f"Validando: {PROMPT_NAME}")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        for error in errors:
            print(f"  ❌ {error}")
        return 1
    print("✅ Validação OK")

    print_section_header(f"Push: {PROMPT_NAME}")
    success = push_prompt_to_langsmith(PROMPT_NAME, prompt_data)
    if not success:
        return 1

    print_section_header("Concluído")
    print(f"✅ Prompt '{PROMPT_NAME}' enviado com sucesso para o LangSmith Hub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
