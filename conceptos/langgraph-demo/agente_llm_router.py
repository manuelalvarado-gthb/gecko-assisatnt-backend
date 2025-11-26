#!/usr/bin/env python3

from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
import sys
import re
import json

class EstadoAgente(TypedDict):
    consulta_usuario: str
    tipo_consulta: str
    resultado_herramienta: str
    requiere_aprobacion: bool
    resultado_final: str

def llm_router_simulado(consulta: str) -> str:
    """
    Simula un LLM router que analiza la consulta y decide la herramienta.
    En un caso real, esto sería una llamada a OpenAI, Anthropic, etc.
    """
    
    # Prompt para el LLM router
    prompt = f"""
    Analiza la siguiente consulta del usuario y decide qué herramienta usar.
    
    Consulta: "{consulta}"
    
    Herramientas disponibles:
    - "calculo": Para operaciones matemáticas, números, cálculos
    - "busqueda": Para buscar información, artículos, datos externos
    - "clima": Para consultas sobre tiempo, temperatura, clima
    - "general": Para saludos, conversación general, otras consultas
    
    Responde SOLO con una de estas opciones: calculo, busqueda, clima, general
    """
    
    # Simulación de respuesta LLM basada en análisis de contenido
    consulta_lower = consulta.lower()
    
    # Lógica más sofisticada que simula decisiones de LLM
    if any(char in consulta for char in "+-*/") or any(word in consulta_lower for word in ["calcular", "suma", "resta", "multiplicar", "dividir", "resultado", "operación"]):
        decision = "calculo"
        razon = "Detecté operaciones matemáticas o palabras relacionadas con cálculos"
    elif any(word in consulta_lower for word in ["buscar", "información", "artículo", "datos", "investigar", "encontrar", "saber sobre"]):
        decision = "busqueda"
        razon = "Detecté intención de búsqueda de información"
    elif any(word in consulta_lower for word in ["clima", "tiempo", "temperatura", "lluvia", "sol", "nublado", "meteorológico"]):
        decision = "clima"
        razon = "Detecté consulta relacionada con el clima"
    else:
        decision = "general"
        razon = "No detecté patrones específicos, clasificando como consulta general"
    
    print(f"🧠 LLM ROUTER: {razon}")
    return decision

def herramienta_busqueda_web(consulta: str) -> str:
    return f"🔍 Resultados de búsqueda para '{consulta}': Encontré 3 artículos relevantes sobre el tema."

def herramienta_calculadora(expresion: str) -> str:
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expresion):
            resultado = eval(expresion)
            return f"🧮 El resultado de {expresion} es: {resultado}"
        else:
            return "❌ Error: Solo operaciones matemáticas básicas"
    except:
        return "❌ Error en el cálculo"

def herramienta_clima(ciudad: str) -> str:
    return f"🌤️ El clima en {ciudad}: 22°C, parcialmente nublado, viento suave."

def nodo_router_llm(estado: EstadoAgente):
    consulta = estado["consulta_usuario"]
    print(f"\n🤖 LLM ROUTER: Analizando '{consulta}'")
    
    # Usar LLM para decidir la herramienta
    tipo = llm_router_simulado(consulta)
    
    herramientas = {
        "calculo": "CALCULADORA",
        "busqueda": "BÚSQUEDA WEB", 
        "clima": "CLIMA",
        "general": "RESPUESTA GENERAL"
    }
    
    print(f"📍 → Herramienta seleccionada: {herramientas[tipo]}")
    return {"tipo_consulta": tipo}

def nodo_herramienta_busqueda(estado: EstadoAgente):
    resultado = herramienta_busqueda_web(estado["consulta_usuario"])
    return {"resultado_herramienta": resultado, "requiere_aprobacion": True}

def nodo_herramienta_calculo(estado: EstadoAgente):
    consulta = estado["consulta_usuario"]
    expresion = re.search(r'[\d+\-*/().\s]+', consulta)
    if expresion:
        resultado = herramienta_calculadora(expresion.group().strip())
    else:
        resultado = "❌ No se encontró expresión matemática válida"
    return {"resultado_herramienta": resultado, "requiere_aprobacion": False}

def nodo_herramienta_clima(estado: EstadoAgente):
    consulta = estado["consulta_usuario"]
    palabras = consulta.split()
    ciudad = "Madrid"
    for i, palabra in enumerate(palabras):
        if palabra.lower() in ["en", "de"] and i + 1 < len(palabras):
            ciudad = palabras[i + 1]
            break
    resultado = herramienta_clima(ciudad)
    return {"resultado_herramienta": resultado, "requiere_aprobacion": True}

def nodo_respuesta_general(estado: EstadoAgente):
    resultado = f"💬 Respuesta general para: {estado['consulta_usuario']}"
    return {"resultado_herramienta": resultado, "requiere_aprobacion": False}

def nodo_revision_humana(estado: EstadoAgente):
    print(f"\n👤 REVISIÓN HUMANA REQUERIDA:")
    print(f"   Consulta: {estado['consulta_usuario']}")
    print(f"   Resultado: {estado['resultado_herramienta']}")
    
    while True:
        respuesta = input("\n¿Aprobar este resultado? (s/n): ").strip().lower()
        if respuesta in ['s', 'si', 'yes', 'y']:
            print("✅ APROBADO")
            return {"resultado_final": estado["resultado_herramienta"]}
        elif respuesta in ['n', 'no']:
            print("❌ RECHAZADO")
            return {"resultado_final": "La respuesta fue rechazada por el supervisor humano."}
        else:
            print("Por favor responda 's' o 'n'")

def nodo_resultado_final(estado: EstadoAgente):
    resultado = estado["resultado_herramienta"]
    print(f"\n✨ RESULTADO FINAL: {resultado}")
    return {"resultado_final": resultado}

def decidir_herramienta(estado: EstadoAgente) -> Literal["busqueda", "calculo", "clima", "general"]:
    return estado["tipo_consulta"]

def decidir_aprobacion(estado: EstadoAgente) -> Literal["revision_humana", "resultado_final"]:
    return "revision_humana" if estado.get("requiere_aprobacion") else "resultado_final"

def crear_agente_llm_router():
    workflow = StateGraph(EstadoAgente)
    
    workflow.add_node("router_llm", nodo_router_llm)
    workflow.add_node("herramienta_busqueda", nodo_herramienta_busqueda)
    workflow.add_node("herramienta_calculo", nodo_herramienta_calculo)
    workflow.add_node("herramienta_clima", nodo_herramienta_clima)
    workflow.add_node("respuesta_general", nodo_respuesta_general)
    workflow.add_node("revision_humana", nodo_revision_humana)
    workflow.add_node("resultado_final", nodo_resultado_final)
    
    workflow.set_entry_point("router_llm")
    
    workflow.add_conditional_edges("router_llm", decidir_herramienta, {
        "busqueda": "herramienta_busqueda",
        "calculo": "herramienta_calculo", 
        "clima": "herramienta_clima",
        "general": "respuesta_general"
    })
    
    workflow.add_conditional_edges("herramienta_busqueda", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_calculo", decidir_aprobacion)
    workflow.add_conditional_edges("herramienta_clima", decidir_aprobacion)
    workflow.add_conditional_edges("respuesta_general", decidir_aprobacion)
    
    workflow.add_edge("revision_humana", END)
    workflow.add_edge("resultado_final", END)
    
    return workflow.compile()

def main():
    if len(sys.argv) < 2:
        print("Uso: python agente_llm_router.py 'tu consulta aquí'")
        print("\nEjemplos:")
        print("  python agente_llm_router.py 'Quiero calcular 25 + 17 multiplicado por 3'")
        print("  python agente_llm_router.py 'Necesito buscar información sobre Python'")
        print("  python agente_llm_router.py 'Me gustaría saber el clima en Barcelona'")
        print("  python agente_llm_router.py 'Hola, ¿cómo estás hoy?'")
        return
    
    consulta = " ".join(sys.argv[1:])
    agente = crear_agente_llm_router()
    
    print("🤖 Demo Agente LangGraph - LLM Router")
    print("=" * 50)
    
    estado_inicial = {
        "consulta_usuario": consulta,
        "tipo_consulta": "",
        "resultado_herramienta": "",
        "requiere_aprobacion": False,
        "resultado_final": ""
    }
    
    agente.invoke(estado_inicial)

if __name__ == "__main__":
    main()
