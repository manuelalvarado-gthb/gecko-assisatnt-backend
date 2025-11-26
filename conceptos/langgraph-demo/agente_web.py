from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import time

class EstadoAgente(TypedDict):
    mensajes: Annotated[list, operator.add]
    consulta_usuario: str
    tipo_consulta: str
    resultado_herramienta: str
    requiere_aprobacion: bool
    aprobacion_humana: str
    resultado_final: str

# Herramientas
def herramienta_busqueda_web(consulta: str) -> str:
    print(f"🔍 Ejecutando búsqueda web para: {consulta}")
    return f"Resultados de búsqueda para '{consulta}': Encontré 3 artículos relevantes sobre el tema."

def herramienta_calculadora(expresion: str) -> str:
    print(f"🧮 Ejecutando cálculo: {expresion}")
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expresion):
            resultado = eval(expresion)
            return f"El resultado de {expresion} es: {resultado}"
        else:
            return "Error: Solo se permiten operaciones matemáticas básicas"
    except:
        return "Error en el cálculo"

def herramienta_clima(ciudad: str) -> str:
    print(f"🌤️ Consultando clima para: {ciudad}")
    return f"El clima en {ciudad}: 22°C, parcialmente nublado, viento suave."

# Nodos
def nodo_router(estado: EstadoAgente):
    consulta = estado["consulta_usuario"].lower()
    print(f"🤖 ROUTER: Analizando consulta: '{estado['consulta_usuario']}'")
    
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
        print("📍 ROUTER: Consulta general")
    
    return {"tipo_consulta": tipo, "mensajes": [f"Router decidió usar: {tipo}"]}

def nodo_herramienta_busqueda(estado: EstadoAgente):
    resultado = herramienta_busqueda_web(estado["consulta_usuario"])
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": True,
        "mensajes": ["Herramienta de búsqueda ejecutada"]
    }

def nodo_herramienta_calculo(estado: EstadoAgente):
    consulta = estado["consulta_usuario"]
    import re
    expresion = re.search(r'[\d+\-*/().\s]+', consulta)
    if expresion:
        resultado = herramienta_calculadora(expresion.group().strip())
    else:
        resultado = "No se pudo extraer una expresión matemática válida"
    
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": False,
        "mensajes": ["Herramienta de cálculo ejecutada"]
    }

def nodo_herramienta_clima(estado: EstadoAgente):
    consulta = estado["consulta_usuario"]
    palabras = consulta.split()
    ciudad = "Madrid"
    for i, palabra in enumerate(palabras):
        if palabra.lower() in ["en", "de"] and i + 1 < len(palabras):
            ciudad = palabras[i + 1]
            break
    
    resultado = herramienta_clima(ciudad)
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": True,
        "mensajes": ["Herramienta de clima ejecutada"]
    }

def nodo_respuesta_general(estado: EstadoAgente):
    resultado = f"Respuesta general para: {estado['consulta_usuario']}"
    return {
        "resultado_herramienta": resultado,
        "requiere_aprobacion": False,
        "mensajes": ["Respuesta general generada"]
    }

def nodo_resultado_final(estado: EstadoAgente):
    if estado.get("requiere_aprobacion") and not estado.get("aprobacion_humana"):
        # Para web, devolver sin procesar - será manejado por la API
        resultado = estado["resultado_herramienta"]
    elif estado.get("aprobacion_humana") == "rechazado":
        resultado = "La respuesta fue rechazada por el supervisor humano."
    else:
        resultado = estado["resultado_herramienta"]
    
    print(f"✨ RESULTADO FINAL: {resultado}")
    return {"resultado_final": resultado}

# Funciones de decisión
def decidir_herramienta(estado: EstadoAgente) -> Literal["busqueda", "calculo", "clima", "general"]:
    return estado["tipo_consulta"]

def decidir_aprobacion(estado: EstadoAgente) -> Literal["resultado_final"]:
    return "resultado_final"

# Crear agente web (sin human-in-the-loop bloqueante)
def crear_agente_web():
    workflow = StateGraph(EstadoAgente)
    
    workflow.add_node("router", nodo_router)
    workflow.add_node("herramienta_busqueda", nodo_herramienta_busqueda)
    workflow.add_node("herramienta_calculo", nodo_herramienta_calculo)
    workflow.add_node("herramienta_clima", nodo_herramienta_clima)
    workflow.add_node("respuesta_general", nodo_respuesta_general)
    workflow.add_node("resultado_final", nodo_resultado_final)
    
    workflow.set_entry_point("router")
    
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
    
    workflow.add_conditional_edges("herramienta_busqueda", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_calculo", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_clima", decidir_aprobacion)
    workflow.add_conditional_edges("respuesta_general", decidir_aprobacion)
    
    workflow.add_edge("resultado_final", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
