#!/bin/bash

if [ $# -eq 0 ]; then
    echo "🤖 LangGraph Agent - Terminal"
    echo "============================="
    echo ""
    echo "Uso: ./invoke.sh 'tu consulta'"
    echo ""
    echo "Ejemplos:"
    echo "  ./invoke.sh 'Calcular 25 + 17 * 3'"
    echo "  ./invoke.sh 'Buscar información sobre Docker'"
    echo "  ./invoke.sh 'Clima en Madrid'"
    echo "  ./invoke.sh 'Hola, ¿cómo estás?'"
    echo ""
    exit 1
fi

# Ejecutar en Docker
docker-compose run --rm langgraph-demo python agente_terminal.py "$@"
