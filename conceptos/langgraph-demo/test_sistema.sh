#!/bin/bash

echo "🧪 Probando Sistema LangGraph"
echo "============================"

# Test 1: Cálculo (automático)
echo "1. Probando cálculo (automático)..."
CALC_RESULT=$(curl -s -X POST http://localhost:8000/consulta -F "consulta=Calcular 15 * 4")
echo "Resultado: $CALC_RESULT"
echo ""

# Test 2: Consulta general (automática)
echo "2. Probando consulta general (automática)..."
GENERAL_RESULT=$(curl -s -X POST http://localhost:8000/consulta -F "consulta=¿Cómo estás?")
echo "Resultado: $GENERAL_RESULT"
echo ""

# Test 3: Búsqueda (requiere aprobación)
echo "3. Probando búsqueda (requiere aprobación)..."
SEARCH_RESULT=$(curl -s -X POST http://localhost:8000/consulta -F "consulta=Buscar información sobre Docker")
echo "Resultado inicial: $SEARCH_RESULT"

# Extraer session_id
SESSION_ID=$(echo $SEARCH_RESULT | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
if [ ! -z "$SESSION_ID" ]; then
    echo "Session ID: $SESSION_ID"
    
    # Aprobar
    echo "Aprobando resultado..."
    APPROVAL_RESULT=$(curl -s -X POST http://localhost:8000/aprobar -F "session_id=$SESSION_ID" -F "aprobacion=si")
    echo "Resultado final: $APPROVAL_RESULT"
fi
echo ""

# Test 4: Clima (requiere aprobación)
echo "4. Probando clima (requiere aprobación)..."
WEATHER_RESULT=$(curl -s -X POST http://localhost:8000/consulta -F "consulta=¿Cuál es el clima en Madrid?")
echo "Resultado inicial: $WEATHER_RESULT"

# Extraer session_id
SESSION_ID=$(echo $WEATHER_RESULT | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
if [ ! -z "$SESSION_ID" ]; then
    echo "Session ID: $SESSION_ID"
    
    # Rechazar
    echo "Rechazando resultado..."
    REJECTION_RESULT=$(curl -s -X POST http://localhost:8000/aprobar -F "session_id=$SESSION_ID" -F "aprobacion=no")
    echo "Resultado final: $REJECTION_RESULT"
fi
echo ""

echo "✅ Todas las pruebas completadas!"
echo "🌐 Interfaz web disponible en: http://localhost:8000"
