"""
JW.org Web Scraper
Extrae datos estructurados de páginas de JW.org
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional

# Configuración
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
TIMEOUT = 15

def extraer_indice_semanas(url: str) -> List[Dict]:
    """
    Extrae lista de semanas del índice de JW.org
    
    Args:
        url: URL del índice
        
    Returns:
        Lista de diccionarios con semanas disponibles
    """
    try:
        print(f"  📡 Conectando a JW.org...")
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        semanas = []
        
        links = soup.find_all('a', href=re.compile(r'programa-reunion|guia-actividades'))
        
        print(f"  🔍 Analizando {len(links)} enlaces encontrados...")
        
        for link in links:
            href = link.get('href', '')
            texto = link.get_text(strip=True)
            
            if texto and re.search(r'\d+-\d+', texto):
                if href.startswith('/'):
                    href = f"https://www.jw.org{href}"
                
                fecha_match = re.search(r'(\d+-\d+\s+de\s+\w+)', texto)
                if fecha_match:
                    fecha = fecha_match.group(1)
                    
                    semanas.append({
                        'titulo': texto,
                        'fecha': fecha,
                        'url': href,
                        'id': generar_id(fecha)
                    })
        
        semanas_unicas = []
        urls_vistas = set()
        
        for semana in semanas:
            if semana['url'] not in urls_vistas:
                semanas_unicas.append(semana)
                urls_vistas.add(semana['url'])
        
        print(f"  ✅ {len(semanas_unicas)} semanas únicas encontradas")
        return semanas_unicas
        
    except requests.Timeout:
        print("  ❌ Timeout: JW.org tardó demasiado en responder")
        return []
    except requests.ConnectionError:
        print("  ❌ Error de conexión")
        return []
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return []

def extraer_datos_semana(url: str) -> Optional[Dict]:
    """
    Extrae datos estructurados de una semana específica
    
    Args:
        url: URL de la página de la semana
        
    Returns:
        Diccionario con todos los datos de la semana
    """
    try:
        print(f"  📡 Descargando página...")
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"  🔍 Parseando estructura HTML...")
        
        datos = {
            'fecha': extraer_fecha(soup),
            'lectura_biblica': extraer_lectura_biblica(soup),
            'cancion_inicial': extraer_cancion(soup, 'inicial'),
            'cancion_intermedia': extraer_cancion(soup, 'intermedia'),
            'cancion_final': extraer_cancion(soup, 'final'),
            'palabras_introduccion': '1',
            'palabras_conclusion': '3',
        }
        
        datos['tesoros_biblia'] = extraer_seccion_tesoros(soup)
        datos['seamos_maestros'] = extraer_seccion_maestros(soup)
        datos['vida_cristiana'] = extraer_seccion_vida(soup)
        
        print(f"  ✅ Datos extraídos: {datos['fecha']}")
        return datos
        
    except Exception as e:
        print(f"  ❌ Error al extraer: {str(e)}")
        return {'error': str(e)}

def extraer_fecha(soup: BeautifulSoup) -> str:
    """Extrae la fecha de la semana"""
    selectores = [
        'h2.contextTitle',
        'h1',
        '.dc-icon--calendar + strong',
        'strong'
    ]
    
    for selector in selectores:
        elemento = soup.select_one(selector)
        if elemento:
            texto = elemento.get_text(strip=True)
            match = re.search(r'(\d+-\d+\s+de\s+\w+)', texto)
            if match:
                return match.group(1)
    
    return "Fecha no encontrada"

def extraer_lectura_biblica(soup: BeautifulSoup) -> str:
    """Extrae la lectura bíblica de la semana"""
    for elemento in soup.find_all(['p', 'li', 'strong']):
        texto = elemento.get_text()
        if 'Lectura de la Biblia' in texto or 'lectura:' in texto.lower():
            match = re.search(r'([A-ZÑÁÉÍÓÚ\s]+\d+(?:-\d+)?)', texto.upper())
            if match:
                return match.group(1).strip()
    
    return "No especificada"

def extraer_cancion(soup: BeautifulSoup, tipo: str) -> str:
    """
    Extrae número de canción
    
    Args:
        tipo: 'inicial', 'intermedia', o 'final'
    """
    canciones = []
    
    for elemento in soup.find_all(text=re.compile(r'Canción\s+\d+', re.IGNORECASE)):
        match = re.search(r'Canción\s+(\d+)', elemento, re.IGNORECASE)
        if match:
            canciones.append(match.group(1))
    
    if tipo == 'inicial' and len(canciones) >= 1:
        return canciones[0]
    elif tipo == 'intermedia' and len(canciones) >= 2:
        return canciones[1]
    elif tipo == 'final' and len(canciones) >= 3:
        return canciones[2]
    
    return "N/A"

def extraer_seccion_tesoros(soup: BeautifulSoup) -> List[Dict]:
    """Extrae partes de Tesoros de la Biblia"""
    return extraer_partes_seccion(soup, 'TESOROS DE LA BIBLIA', hora_inicio='19:06')

def extraer_seccion_maestros(soup: BeautifulSoup) -> List[Dict]:
    """Extrae partes de Seamos Mejores Maestros"""
    return extraer_partes_seccion(soup, 'SEAMOS MEJORES MAESTROS', hora_inicio='19:30')

def extraer_seccion_vida(soup: BeautifulSoup) -> List[Dict]:
    """Extrae partes de Nuestra Vida Cristiana"""
    return extraer_partes_seccion(soup, 'NUESTRA VIDA CRISTIANA', hora_inicio='19:47')

def extraer_partes_seccion(soup: BeautifulSoup, nombre_seccion: str, hora_inicio: str) -> List[Dict]:
    """
    Extrae todas las partes de una sección específica
    
    Args:
        soup: Objeto BeautifulSoup
        nombre_seccion: Nombre de la sección a buscar
        hora_inicio: Hora de inicio de la sección
    """
    partes = []
    hora_actual = convertir_hora_a_minutos(hora_inicio)
    numero_parte = 1
    
    seccion = None
    for header in soup.find_all(['h2', 'h3', 'strong']):
        if nombre_seccion in header.get_text().upper():
            seccion = header.parent
            break
    
    if not seccion:
        print(f"  ⚠️ No se encontró sección: {nombre_seccion}")
        return []
    
    lista = seccion.find_next('ul') or seccion.find_next('ol')
    if not lista:
        return []
    
    items = lista.find_all('li', recursive=False)
    
    for item in items:
        texto = item.get_text(strip=True)
        
        duracion_match = re.search(r'\(?\s*(\d+)\s*min', texto, re.IGNORECASE)
        duracion = duracion_match.group(1) if duracion_match else '5'
        
        titulo = re.sub(r'\(?\s*\d+\s*min[s.]?\)?', '', texto, flags=re.IGNORECASE)
        titulo = titulo.strip(' .,:')
        
        rol = None
        if 'conversación' in titulo.lower() or 'revisita' in titulo.lower() or 'discípulo' in titulo.lower():
            rol = 'Est./Ayud.:'
        elif 'Lectura' in titulo:
            rol = 'Estudiante:'
        elif 'Estudio bíblico' in titulo:
            rol = 'Conductor/Lector:'
        
        hora = minutos_a_hora(hora_actual)
        
        partes.append({
            'numero': numero_parte,
            'hora': hora,
            'titulo': titulo,
            'duracion': duracion,
            'rol': rol
        })
        
        hora_actual += int(duracion)
        numero_parte += 1
    
    return partes

def convertir_hora_a_minutos(hora: str) -> int:
    """Convierte hora HH:MM a minutos totales"""
    try:
        h, m = hora.split(':')
        return int(h) * 60 + int(m)
    except:
        return 0

def minutos_a_hora(minutos: int) -> str:
    """Convierte minutos totales a formato HH:MM"""
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

def generar_id(fecha: str) -> str:
    """Genera ID único desde fecha"""
    return fecha.lower().replace(' de ', '-').replace(' ', '-')
