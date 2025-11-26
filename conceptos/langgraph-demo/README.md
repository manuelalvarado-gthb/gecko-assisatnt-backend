# Demo Agente LangGraph

Sistema Multi-Agente con Router, Herramientas y Human-in-the-Loop

## 🚀 Características

- **Router Inteligente**: Analiza consultas y dirige al agente apropiado
- **Múltiples Herramientas**: Búsqueda web, calculadora, clima
- **Human-in-the-Loop**: Revisión humana para operaciones críticas
- **Interfaz Web**: Interfaz amigable para interactuar con el agente
- **Modo Consola**: También disponible para uso en terminal

## 🛠️ Herramientas Disponibles

1. **🔍 Búsqueda Web**: Para consultas de información (requiere aprobación)
2. **🧮 Calculadora**: Para operaciones matemáticas (automática)
3. **🌤️ Clima**: Para consultas meteorológicas (requiere aprobación)
4. **💬 General**: Para consultas generales (automática)

## 📋 Ejemplos de Consultas

- "Buscar información sobre inteligencia artificial"
- "Calcular 25 + 17 * 3"
- "¿Cuál es el clima en Barcelona?"
- "¿Cómo estás hoy?"

## 🐳 Instalación con Docker

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar o descargar los archivos
cd langgraph-demo

# Construir y ejecutar
docker-compose up --build

# Acceder a la aplicación
# Interfaz web: http://localhost:8000
```

### Opción 2: Docker Manual

```bash
# Construir imagen
docker build -t langgraph-demo .

# Ejecutar contenedor
docker run -p 8000:8000 -it langgraph-demo

# Para modo interactivo en consola
docker run -it langgraph-demo python agente_demo.py
```

## 🌐 Uso de la Interfaz Web

1. Abrir navegador en `http://localhost:8000`
2. Seleccionar un ejemplo o escribir consulta personalizada
3. Hacer clic en "Enviar Consulta"
4. Si requiere aprobación humana, revisar y aprobar/rechazar
5. Ver el resultado final

## 💻 Uso en Consola

```bash
# Ejecutar en modo consola
docker run -it langgraph-demo python agente_demo.py
```

## 🔄 Flujo del Sistema

```
Usuario → Router → Herramienta → [Revisión Humana] → Resultado Final
```

### Detalle del Flujo:

1. **Router**: Analiza la consulta del usuario
   - Palabras clave para búsqueda: "buscar", "información", "artículo"
   - Palabras clave para cálculo: "calcular", "suma", "+", "multiplicar"
   - Palabras clave para clima: "clima", "tiempo", "temperatura"

2. **Herramientas**: Ejecutan la acción específica
   - Búsqueda: Simula búsqueda web
   - Calculadora: Evalúa expresiones matemáticas
   - Clima: Consulta información meteorológica

3. **Human-in-the-Loop**: Revisión selectiva
   - Búsquedas web: Requieren aprobación
   - Consultas de clima: Requieren aprobación
   - Cálculos: Automáticos
   - Consultas generales: Automáticas

4. **Resultado Final**: Entrega respuesta al usuario

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Usuario       │
└─────────┬───────┘
          │
┌─────────▼───────┐
│   Router        │ ← Decide qué herramienta usar
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐   ┌─────────┐   ┌─────────┐
│Búsqueda│   │Cálculo│   │ Clima   │   │General  │
└───┬───┘   └───┬───┘   └────┬────┘   └────┬────┘
    │           │            │             │
    └─────┬─────┴────────────┴─────────────┘
          │
┌─────────▼───────┐
│ Human Review    │ ← Solo para operaciones críticas
│ (Opcional)      │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Resultado Final │
└─────────────────┘
```

## 📁 Estructura del Proyecto

```
langgraph-demo/
├── agente_demo.py      # Lógica principal del agente
├── app.py              # Aplicación FastAPI
├── templates/
│   └── index.html      # Interfaz web
├── Dockerfile          # Configuración Docker
├── docker-compose.yml  # Orquestación Docker
├── requirements.txt    # Dependencias Python
└── README.md          # Este archivo
```

## 🔧 Personalización

### Agregar Nueva Herramienta

1. Crear función de herramienta en `agente_demo.py`
2. Agregar nodo en el grafo
3. Actualizar router con nuevas palabras clave
4. Configurar si requiere aprobación humana

### Modificar Lógica de Aprobación

Editar la función `decidir_aprobacion()` para cambiar qué operaciones requieren revisión humana.

## 🐛 Troubleshooting

### Puerto ocupado
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto 8001 en lugar de 8000
```

### Problemas de permisos
```bash
# Ejecutar con sudo si es necesario
sudo docker-compose up --build
```

### Ver logs
```bash
# Ver logs del contenedor
docker-compose logs -f
```

## 📚 Conceptos Demostrados

- **StateGraph**: Grafo de estados de LangGraph
- **Nodos**: Funciones de procesamiento
- **Aristas Condicionales**: Decisiones de flujo
- **Checkpointer**: Persistencia de estado
- **Human-in-the-Loop**: Intervención humana
- **Router Pattern**: Enrutamiento inteligente
- **Tool Integration**: Integración de herramientas
