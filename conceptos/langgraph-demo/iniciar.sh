#!/bin/bash

echo "🤖 Demo Agente LangGraph"
echo "======================="
echo ""
echo "Seleccione una opción:"
echo "1. Interfaz Web (recomendado)"
echo "2. Modo Consola Interactivo"
echo "3. Construir imagen Docker"
echo "4. Ver logs"
echo ""

read -p "Opción (1-4): " opcion

case $opcion in
    1)
        echo "🌐 Iniciando interfaz web..."
        echo "Acceder a: http://localhost:8000"
        docker-compose up --build
        ;;
    2)
        echo "💻 Iniciando modo consola..."
        docker-compose run --rm langgraph-demo python agente_demo.py
        ;;
    3)
        echo "🔨 Construyendo imagen..."
        docker-compose build
        echo "✅ Imagen construida"
        ;;
    4)
        echo "📋 Mostrando logs..."
        docker-compose logs -f
        ;;
    *)
        echo "❌ Opción no válida"
        ;;
esac
