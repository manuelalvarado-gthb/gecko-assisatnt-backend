from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from agente_web import crear_agente_web, EstadoAgente
import json
import os
import time

app = FastAPI(title="Demo Agente LangGraph")
templates = Jinja2Templates(directory="templates")

# Crear agente web (sin bloqueos)
agente = crear_agente_web()
sesiones_pendientes = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/consulta")
async def procesar_consulta(consulta: str = Form(...)):
    """Procesa una consulta del usuario"""
    
    config = {"configurable": {"thread_id": f"web-{id(consulta)}"}}
    
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
    
    # Si requiere aprobación, devolver para revisión
    if resultado.get("requiere_aprobacion") and not resultado.get("aprobacion_humana"):
        session_id = f"session_{int(time.time())}_{id(consulta)}"
        sesiones_pendientes[session_id] = {
            "estado": resultado,
            "config": config,
            "consulta": consulta
        }
        
        return {
            "tipo": "aprobacion_requerida",
            "session_id": session_id,
            "consulta": consulta,
            "resultado_herramienta": resultado["resultado_herramienta"],
            "tipo_consulta": resultado["tipo_consulta"]
        }
    
    return {
        "tipo": "completado",
        "resultado": resultado.get("resultado_final", resultado.get("resultado_herramienta", "Sin resultado")),
        "tipo_consulta": resultado["tipo_consulta"]
    }

@app.post("/aprobar")
async def aprobar_resultado(session_id: str = Form(...), aprobacion: str = Form(...)):
    """Maneja la aprobación humana"""
    
    if session_id not in sesiones_pendientes:
        return {"error": "Sesión no encontrada"}
    
    sesion = sesiones_pendientes[session_id]
    
    # Crear nuevo estado con aprobación
    nuevo_estado = sesion["estado"].copy()
    nuevo_estado["aprobacion_humana"] = "aprobado" if aprobacion == "si" else "rechazado"
    
    # Ejecutar nodo final
    if aprobacion == "si":
        resultado_final = nuevo_estado["resultado_herramienta"]
    else:
        resultado_final = "La respuesta fue rechazada por el supervisor humano."
    
    # Limpiar sesión
    del sesiones_pendientes[session_id]
    
    return {
        "tipo": "completado",
        "resultado": resultado_final,
        "aprobado": aprobacion == "si"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
