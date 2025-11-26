#!/bin/bash

if [ $# -eq 0 ]; then
    echo "🧠 LangGraph Agent - LLM Router"
    echo "==============================="
    echo ""
    echo "Uso: ./invoke_llm.sh 'tu consulta'"
    echo ""
    echo "Ejemplos:"
    echo "  ./invoke_llm.sh 'Quiero calcular 25 + 17 multiplicado por 3'"
    echo "  ./invoke_llm.sh 'Necesito buscar información sobre Docker'"
    echo "  ./invoke_llm.sh 'Me gustaría saber el clima en Madrid'"
    echo "  ./invoke_llm.sh 'Hola, ¿cómo estás hoy?'"
    echo ""
    exit 1
fi

# Ejecutar en Docker con LLM router
docker-compose run --rm langgraph-demo python agente_llm_router.py "$@"
