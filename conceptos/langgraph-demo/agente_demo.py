from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import time
import requests

class EstadoAgente(TypedDict):
    mensajes: Annotated[list, operator.add]
    consulta_usuario: str
    tipo_consulta: str
    resultado_herramienta: str
    requiere_aprobacion: bool
    aprobacion_humana: str
    resultado_final: str

# Herramientas simuladas
def herramienta_busqueda_web(consulta: str) -> str:
    """Simula búsqueda web"""
    print(f"🔍 Ejecutando búsqueda web para: {consulta}")
    time.sleep(1)
    return f"Resultados de búsqueda para '{consulta}': Encontré 3 artículos relevantes sobre el tema."

def herramienta_calculadora(expresion: str) -> str:
    """Calculadora simple"""
    print(f"🧮 Ejecutando cálculo: {expresion}")
    try:
        # Solo permite operaciones básicas seguras
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expresion):
            resultado = eval(expresion)
            return f"El resultado de {expresion} es: {resultado}"
        else:
            return "Error: Solo se permiten operaciones matemáticas básicas"
    except:
        return "Error en el cálculo"

def herramienta_clima(ciudad: str) -> str:
    """Simula consulta del clima"""
    print(f"🌤️ Consultando clima para: {ciudad}")
    time.sleep(1)
    return f"El clima en {ciudad}: 22°C, parcialmente nublado, viento suave."

# Nodos del grafo
def nodo_router(estado: EstadoAgente):
    """Router que decide qué herramienta usar"""
    consulta = estado["consulta_usuario"].lower()
    
    print(f"\n🤖 ROUTER: Analizando consulta: '{estado['consulta_usuario']}'")
    
    if any(palabra in consulta for palabra in ["buscar", "información", "artículo"]):
        tipo = "busqueda"
        print("📍 ROUTER: Dirigiendo a herramienta de BÚSQUEDA WEB")
    elif any(palabra in consulta for palabra in ["calcular", "suma", "resta", "multiplicar", "+"]):
        tipo = "calculo"
        print("📍 ROUTER: Dirigiendo a herramienta de CALCULADORA")
    elif any(palabra in consulta for palabra in ["clima", "tiempo", "temperatura"]):
        tipo = "clima"
        print("📍 ROUTER: Dirigiendo a herramienta de CLIMA")
    else:
        tipo = "general"
        print("📍 ROUTER: Consulta general, no requiere herramienta específica")
    
    return {
        "tipo_consulta": tipo,
        "mensajes": [f"Router decidió usar: {tipo}"]
    }

def nodo_herramienta_busqueda(estado: EstadoAgente):
    """Ejecuta búsqueda web"""
    resultado = herramienta_busqueda_web(estado["consulta_usuario"])
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": True,  # Búsquedas requieren aprobación
        "mensajes": ["Herramienta de búsqueda ejecutada"]
    }

def nodo_herramienta_calculo(estado: EstadoAgente):
    """Ejecuta cálculos"""
    # Extraer expresión matemática de la consulta
    consulta = estado["consulta_usuario"]
    # Buscar números y operadores
    import re
    expresion = re.search(r'[\d+\-*/().\s]+', consulta)
    if expresion:
        resultado = herramienta_calculadora(expresion.group().strip())
    else:
        resultado = "No se pudo extraer una expresión matemática válida"
    
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": False,  # Cálculos no requieren aprobación
        "mensajes": ["Herramienta de cálculo ejecutada"]
    }

def nodo_herramienta_clima(estado: EstadoAgente):
    """Consulta el clima"""
    # Extraer ciudad de la consulta
    consulta = estado["consulta_usuario"]
    palabras = consulta.split()
    ciudad = "Madrid"  # Ciudad por defecto
    for i, palabra in enumerate(palabras):
        if palabra.lower() in ["en", "de"] and i + 1 < len(palabras):
            ciudad = palabras[i + 1]
            break
    
    resultado = herramienta_clima(ciudad)
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": True,  # Clima requiere aprobación
        "mensajes": ["Herramienta de clima ejecutada"]
    }

def nodo_respuesta_general(estado: EstadoAgente):
    """Respuesta para consultas generales"""
    resultado = f"Respuesta general para: {estado['consulta_usuario']}"
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": False,
        "mensajes": ["Respuesta general generada"]
    }

def nodo_revision_humana(estado: EstadoAgente):
    """Punto de intervención humana"""
    print(f"\n👤 REVISIÓN HUMANA REQUERIDA")
    print(f"Consulta: {estado['consulta_usuario']}")
    print(f"Resultado de herramienta: {estado['resultado_herramienta']}")
    
    # Si ya hay una aprobación (desde web), usarla
    if estado.get("aprobacion_humana"):
        aprobacion = estado["aprobacion_humana"]
        if aprobacion == "aprobado":
            print("✅ APROBADO por humano")
            return {
                "aprobacion_humana": "aprobado",
                "mensajes": ["Resultado aprobado por humano"]
            }
        else:
            print("❌ RECHAZADO por humano")
            return {
                "aprobacion_humana": "rechazado",
                "mensajes": ["Resultado rechazado por humano"]
            }
    
    # Solo pedir input si estamos en modo consola
    try:
        print("\n¿Aprobar este resultado? (s/n): ", end="")
        aprobacion = input().strip().lower()
        
        if aprobacion in ['s', 'si', 'yes', 'y']:
            print("✅ APROBADO por humano")
            return {
                "aprobacion_humana": "aprobado",
                "mensajes": ["Resultado aprobado por humano"]
            }
        else:
            print("❌ RECHAZADO por humano")
            return {
                "aprobacion_humana": "rechazado",
                "mensajes": ["Resultado rechazado por humano"]
            }
    except:
        # Si no se puede obtener input (modo web), marcar como pendiente
        print("⏳ Esperando aprobación humana...")
        return {
            "aprobacion_humana": "pendiente",
            "mensajes": ["Esperando aprobación humana"]
        }

def nodo_resultado_final(estado: EstadoAgente):
    """Genera el resultado final"""
    if estado.get("requiere_aprobacion") and estado.get("aprobacion_humana") == "rechazado":
        resultado = "La respuesta fue rechazada por el supervisor humano. Por favor, reformule su consulta."
    else:
        resultado = estado["resultado_herramienta"]
    
    print(f"\n✨ RESULTADO FINAL: {resultado}")
    return {"resultado_final": resultado}

# Funciones de decisión para aristas condicionales
def decidir_herramienta(estado: EstadoAgente) -> Literal["busqueda", "calculo", "clima", "general"]:
    return estado["tipo_consulta"]

def decidir_aprobacion(estado: EstadoAgente) -> Literal["revision_humana", "resultado_final"]:
    if estado.get("requiere_aprobacion", False):
        return "revision_humana"
    return "resultado_final"

def decidir_despues_revision(estado: EstadoAgente) -> Literal["resultado_final"]:
    # Si la aprobación está pendiente, no continuar (para modo web)
    if estado.get("aprobacion_humana") == "pendiente":
        return "resultado_final"  # Esto será manejado por la app web
    return "resultado_final"

# Crear el grafo
def crear_agente():
    workflow = StateGraph(EstadoAgente)
    
    # Agregar nodos
    workflow.add_node("router", nodo_router)
    workflow.add_node("herramienta_busqueda", nodo_herramienta_busqueda)
    workflow.add_node("herramienta_calculo", nodo_herramienta_calculo)
    workflow.add_node("herramienta_clima", nodo_herramienta_clima)
    workflow.add_node("respuesta_general", nodo_respuesta_general)
    workflow.add_node("revision_humana", nodo_revision_humana)
    workflow.add_node("resultado_final", nodo_resultado_final)
    
    # Definir punto de entrada
    workflow.set_entry_point("router")
    
    # Aristas condicionales desde router
    workflow.add_conditional_edges(
        "router",
        decidir_herramienta,
        {
            "busqueda": "herramienta_busqueda",
            "calculo": "herramienta_calculo", 
            "clima": "herramienta_clima",
            "general": "respuesta_general"
        }
    )
    
    # Aristas desde herramientas hacia decisión de aprobación
    workflow.add_conditional_edges("herramienta_busqueda", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_calculo", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_clima", decidir_aprobacion)
    workflow.add_conditional_edges("respuesta_general", decidir_aprobacion)
    
    # Arista desde revisión humana
    workflow.add_conditional_edges("revision_humana", decidir_despues_revision)
    
    # Arista final
    workflow.add_edge("resultado_final", END)
    
    # Compilar con memoria para persistencia
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

def ejecutar_consulta(agente, consulta: str):
    """Ejecuta una consulta en el agente"""
    print(f"\n{'='*60}")
    print(f"🚀 NUEVA CONSULTA: {consulta}")
    print(f"{'='*60}")
    
    config = {"configurable": {"thread_id": "demo-thread"}}
    
    estado_inicial = {
        "consulta_usuario": consulta,
        "mensajes": [],
        "tipo_consulta": "",
        "resultado_herramienta": "",
        "requiere_aprobacion": False,
        "aprobacion_humana": "",
        "resultado_final": ""
    }
    
    # Ejecutar el agente
    resultado = agente.invoke(estado_inicial, config)
    
    return resultado["resultado_final"]

if __name__ == "__main__":
    print("🤖 Iniciando Demo de Agente LangGraph")
    print("=====================================")
    
    # Crear agente
    agente = crear_agente()
    
    # Consultas de ejemplo
    consultas_ejemplo = [
        "Buscar información sobre inteligencia artificial",
        "Calcular 25 + 17 * 3",
        "¿Cuál es el clima en Barcelona?",
        "¿Cómo estás hoy?"
    ]
    
    print("\n📋 Consultas de ejemplo disponibles:")
    for i, consulta in enumerate(consultas_ejemplo, 1):
        print(f"{i}. {consulta}")
    
    while True:
        print(f"\n{'='*60}")
        print("Opciones:")
        print("1-4: Ejecutar consulta de ejemplo")
        print("c: Consulta personalizada")
        print("q: Salir")
        
        opcion = input("\nSeleccione una opción: ").strip().lower()
        
        if opcion == 'q':
            print("👋 ¡Hasta luego!")
            break
        elif opcion in ['1', '2', '3', '4']:
            consulta = consultas_ejemplo[int(opcion) - 1]
            ejecutar_consulta(agente, consulta)
        elif opcion == 'c':
            consulta = input("Ingrese su consulta: ").strip()
            if consulta:
                ejecutar_consulta(agente, consulta)
        else:
            print("❌ Opción no válida")
