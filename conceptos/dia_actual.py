from datetime import datetime
import locale
import requests

# Configurar locale a español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_MX.UTF-8')
    except:
        pass

# Obtener fecha actual
ahora = datetime.now()

# Obtener ubicación por IP
try:
    response = requests.get('http://ip-api.com/json/')
    data = response.json()
    ciudad = data.get('city', 'Desconocida')
    pais = data.get('country', 'Desconocido')
    region = data.get('regionName', '')
    
    print(f"📍 Ubicación: {ciudad}, {region}, {pais}")
except:
    print("📍 No se pudo obtener la ubicación")

print(f"📅 Hoy es {ahora.strftime('%A, %d de %B de %Y')}")
print(f"🕐 Hora actual: {ahora.strftime('%H:%M:%S')}")
