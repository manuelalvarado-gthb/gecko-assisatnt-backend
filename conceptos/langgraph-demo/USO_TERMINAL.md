# 🚀 Uso del Agente LangGraph en Terminal

## Comando Simple:

```bash
./invoke.sh "tu consulta aquí"
```

## 📋 Ejemplos de Uso:

### 1. Cálculos (Automáticos)
```bash
./invoke.sh "Calcular 25 + 17 * 3"
./invoke.sh "15 + 25 * 2"
./invoke.sh "100 / 4 + 10"
```

### 2. Consultas Generales (Automáticas)
```bash
./invoke.sh "Hola, ¿cómo estás?"
./invoke.sh "¿Qué tal el día?"
./invoke.sh "Cuéntame algo interesante"
```

### 3. Búsquedas (Requieren Aprobación)
```bash
./invoke.sh "Buscar información sobre Python"
./invoke.sh "Buscar artículos sobre Docker"
./invoke.sh "Información sobre LangGraph"
```

### 4. Clima (Requiere Aprobación)
```bash
./invoke.sh "Clima en Madrid"
./invoke.sh "¿Cuál es el clima en Barcelona?"
./invoke.sh "Tiempo en Valencia"
```

## 🔄 Flujo Demostrado:

1. **Router** analiza tu consulta
2. **Herramienta** específica se ejecuta
3. **Human-in-the-Loop** (si es necesario)
4. **Resultado final**

## 👤 Aprobación Humana:

Para búsquedas y clima, el sistema te preguntará:
```
¿Aprobar este resultado? (s/n):
```
- Escribe `s` para aprobar
- Escribe `n` para rechazar

## ⚡ Inicio Rápido:

```bash
# Navegar al directorio
cd langgraph-demo

# Probar cálculo
./invoke.sh "Calcular 10 + 5"

# Probar búsqueda (requerirá tu aprobación)
./invoke.sh "Buscar información sobre IA"
```

¡Listo para usar! 🎉
