#!/usr/bin/env python3

from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
import sys
import re

class EstadoAgente(TypedDict):
    consulta_usuario: str
    tipo_consulta: str
    resultado_herramienta: str
    requiere_aprobacion: bool
    resultado_final: str

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

def nodo_router(estado: EstadoAgente):
    consulta = estado["consulta_usuario"].lower()
    print(f"\n🤖 ROUTER: Analizando '{estado['consulta_usuario']}'")
    
    if any(palabra in consulta for palabra in ["buscar", "información", "artículo"]):
        tipo = "busqueda"
        print("📍 → Herramienta de BÚSQUEDA WEB")
    elif any(palabra in consulta for palabra in ["calcular", "suma", "resta", "multiplicar", "+", "-", "*", "/"]):
        tipo = "calculo"
        print("📍 → Herramienta de CALCULADORA")
    elif any(palabra in consulta for palabra in ["clima", "tiempo", "temperatura"]):
        tipo = "clima"
        print("📍 → Herramienta de CLIMA")
    else:
        tipo = "general"
        print("📍 → Respuesta GENERAL")
    
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

def crear_agente_terminal():
    workflow = StateGraph(EstadoAgente)
    
    workflow.add_node("router", nodo_router)
    workflow.add_node("herramienta_busqueda", nodo_herramienta_busqueda)
    workflow.add_node("herramienta_calculo", nodo_herramienta_calculo)
    workflow.add_node("herramienta_clima", nodo_herramienta_clima)
    workflow.add_node("respuesta_general", nodo_respuesta_general)
    workflow.add_node("revision_humana", nodo_revision_humana)
    workflow.add_node("resultado_final", nodo_resultado_final)
    
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges("router", decidir_herramienta, {
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
        print("Uso: python agente_terminal.py 'tu consulta aquí'")
        print("\nEjemplos:")
        print("  python agente_terminal.py 'Calcular 25 + 17 * 3'")
        print("  python agente_terminal.py 'Buscar información sobre Python'")
        print("  python agente_terminal.py 'Clima en Barcelona'")
        print("  python agente_terminal.py 'Hola, ¿cómo estás?'")
        return
    
    consulta = " ".join(sys.argv[1:])
    agente = crear_agente_terminal()
    
    print("🤖 Demo Agente LangGraph - Terminal")
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
