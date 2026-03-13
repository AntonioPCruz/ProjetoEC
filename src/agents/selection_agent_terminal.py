#!/usr/bin/env python3
"""Interactive terminal test for tool selection agent.
Run this to manually test the agent with your own questions.
"""

from tool_selection_agent import select_tool


def main():
    print("=" * 80)
    print("TESTE INTERATIVO - AGENTE DE SELEÇÃO DE FERRAMENTAS")
    print("=" * 80)

    while True:
        try:
            question = input("\nPergunta: ").strip()

            if not question:
                continue

            if question.lower() in ["sair", "exit", "quit", "q"]:
                print("\nA encerrar... Até logo!")
                break

            print("\nA analisar...")
            result = select_tool(question)

            print(f"  Ferramenta: {result['tool'] or 'NONE'}")
            print(f"  Query: {result['query']}")
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo utilizador. Até logo!")
            break
        except Exception as e:
            print(f"\nErro: {e}")
            print("Certifique-se de que o Ollama está a correr: ollama serve")
            print("-" * 80)


if __name__ == "__main__":
    main()
