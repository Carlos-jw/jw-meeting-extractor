"""
JW.org Web Scraper - Versión Completa
Extrae datos de todas las semanas y genera HTML formateado
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Connection': 'keep-alive'
}

TIMEOUT = 30
MAX_REINTENTOS = 3

LIBROS_BIBLIA = (
    'ECLESIASTÉS', 'GÉNESIS', 'ÉXODO', 'LEVÍTICO', 'NÚMEROS', 'DEUTERONOMIO',
    'JOSUÉ', 'JUECES', 'RUT', 'SAMUEL', 'REYES', 'CRÓNICAS', 'ESDRAS',
    'NEHEMÍAS', 'ESTER', 'JOB', 'SALMOS', 'PROVERBIOS', 'CANTARES',
    'ISAÍAS', 'JEREMÍAS', 'LAMENTACIONES', 'EZEQUIEL', 'DANIEL',
    'OSEAS', 'JOEL', 'AMÓS', 'ABDÍAS', 'JONÁS', 'MIQUEAS', 'NAHÚM',
    'HABACUC', 'SOFONÍAS', 'HAGEO', 'ZACARÍAS', 'MALAQUÍAS',
    'MATEO', 'MARCOS', 'LUCAS', 'JUAN', 'HECHOS', 'ROMANOS',
    'CORINTIOS', 'GÁLATAS', 'EFESIOS', 'FILIPENSES', 'COLOSENSES',
    'TESALONICENSES', 'TIMOTEO', 'TITO', 'FILEMÓN', 'HEBREOS',
    'SANTIAGO', 'PEDRO', 'JUDAS', 'APOCALIPSIS'
)

PATRONES = {
    'fecha': re.compile(r'\d{1,2}\s*(?:-\s*\d{1,2}|de\s+\w+\s+(?:a|al)\s+\d{1,2})\s+de\s+\w+', re.IGNORECASE),
    'cancion': re.compile(r'Canción\s+(\d+)', re.IGNORECASE),
    'palabras': re.compile(r'Palabras\s+de\s+(introducción|conclusión)\s*[:\(]?\s*(\d+)\s*min', re.IGNORECASE),
    'parte_numerada': re.compile(r'^(\d+)\.\s*([^\n(]+?)\s*\((\d+)\s*min', re.MULTILINE | re.IGNORECASE),
}

# ==================== EXTRACCIÓN DE ENLACES ====================

def obtener_enlaces_semanas(url_indice: str) -> List[Dict[str, str]]:
    """
    Extrae todos los enlaces de semanas desde la URL índice.
    
    Args:
        url_indice: URL del índice (ej: .../marzo-abril-2026-mwb/)
        
    Returns:
        Lista de dicts con 'titulo' y 'url' de cada semana
    """
    try:
        print("🔍 Buscando todas las semanas disponibles...\n")
        response = requests.get(url_indice, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        enlaces = []
        
        # Buscar en el contenido principal
        main_content_div = soup.find('div', class_='docPart')
        if main_content_div:
            links = main_content_div.find_all('a', href=True)
        else:
            links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            texto = link.get_text(strip=True)
            
            # Filtrar enlaces válidos de semanas
            if '/es/biblioteca/guia-actividades-reunion-testigos-jehova/' in href and texto:
                # Excluir el índice mismo
                if href != url_indice and not href.endswith('/mwb/'):
                    # Verificar que tenga formato de fecha
                    if PATRONES['fecha'].search(texto):
                        if not href.startswith('http'):
                            href = f"https://www.jw.org{href}"
                        enlaces.append({'titulo': texto, 'url': href})
        
        # Ordenar cronológicamente
        enlaces.sort(key=lambda x: extraer_fecha_para_ordenar(x['titulo']))
        
        print(f"✅ Se encontraron {len(enlaces)} semanas\n")
        return enlaces
        
    except Exception as e:
        print(f"❌ Error al obtener enlaces: {e}")
        return []

def extraer_fecha_para_ordenar(titulo: str) -> tuple:
    """Extrae la fecha inicial para ordenar cronológicamente."""
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    match = re.search(r'(\d{1,2})[- ].*?de\s+(\w+)', titulo, re.IGNORECASE)
    if match:
        dia = int(match.group(1))
        mes_texto = match.group(2).lower()
        mes = meses.get(mes_texto, 0)
        return (mes, dia)
    return (0, 0)

# ==================== EXTRACCIÓN DE CONTENIDO ====================

def obtener_contenido(url: str) -> Optional[str]:
    """Descarga y extrae texto de la página web con reintentos."""
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            main = soup.find('main') or soup
            return main.get_text(separator='\n', strip=True)
        except requests.Timeout:
            if intento == MAX_REINTENTOS:
                print(f"⏱️ Timeout en intento {intento}")
        except requests.RequestException as e:
            if intento == MAX_REINTENTOS:
                print(f"❌ Error: {e}")
    return None

def extraer_fecha_correcta(contenido: str) -> str:
    """Extrae la fecha de la semana del contenido."""
    lineas = contenido.split('\n')
    
    # Buscar en las primeras 20 líneas (cabecera)
    for linea in lineas[:20]:
        fecha_match = PATRONES['fecha'].search(linea)
        if fecha_match:
            return fecha_match.group(0).strip()
    
    # Fallback: buscar en todo el documento
    fecha_match = PATRONES['fecha'].search(contenido)
    if fecha_match:
        return fecha_match.group(0).strip()
    
    return 'Fecha no encontrada'

def extraer_lectura_biblica(contenido: str) -> str:
    """Extrae la lectura bíblica de la semana."""
    for libro in LIBROS_BIBLIA:
        patron = rf'({libro})\s*\d+(?::\d+)?(?:[-–]\d+(?::\d+)?)?'
        match = re.search(patron, contenido, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r'\s+', ' ', match.group(0)).strip()
    
    # Fallback: buscar patrón "Lectura bíblica:"
    match2 = re.search(
        r'Lectura\s+b[ií]blica\s*[:\-]?\s*([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s:–\-]+)',
        contenido, re.IGNORECASE
    )
    return re.sub(r'\s+', ' ', match2.group(1)).strip() if match2 else 'No especificada'

def extraer_canciones(contenido: str) -> Dict[str, str]:
    """Extrae números de las 3 canciones."""
    nums = PATRONES['cancion'].findall(contenido)
    return {
        'inicial': nums[0] if len(nums) > 0 else 'N/A',
        'intermedia': nums[1] if len(nums) > 1 else 'N/A',
        'final': nums[2] if len(nums) > 2 else 'N/A'
    }

def encontrar_posicion_cancion_intermedia(contenido: str) -> int:
    """Encuentra después de qué número de parte viene la canción intermedia."""
    canciones = list(PATRONES['cancion'].finditer(contenido))
    if len(canciones) < 2:
        return 6  # Valor por defecto
    
    pos_cancion = canciones[1].start()
    partes_antes = []
    
    for match in PATRONES['parte_numerada'].finditer(contenido):
        if match.start() < pos_cancion:
            partes_antes.append(int(match.group(1)))
    
    return max(partes_antes) if partes_antes else 6

def extraer_partes(contenido: str) -> Dict[str, List[Dict]]:
    """
    Extrae y clasifica partes dinámicamente según posición de canciones.
    
    Returns:
        Dict con 3 listas: tesoros_biblia, seamos_maestros, vida_cristiana
    """
    parte_antes_cancion = encontrar_posicion_cancion_intermedia(contenido)
    
    secciones = {
        'tesoros_biblia': [],
        'seamos_maestros': [],
        'vida_cristiana': []
    }
    
    contador_parte = 0
    
    # Extraer partes numeradas (1., 2., 3., etc.)
    for match in PATRONES['parte_numerada'].finditer(contenido):
        num = int(match.group(1))
        contador_parte += 1
        
        titulo = match.group(2).strip()
        duracion = int(match.group(3))
        
        # Determinar rol según título
        rol = determinar_rol(titulo)
        
        parte = {
            'numero': contador_parte,
            'titulo': titulo,
            'duracion': duracion,
            'rol': rol
        }
        
        # Clasificar según posición
        if num <= 3:
            secciones['tesoros_biblia'].append(parte)
        elif num <= parte_antes_cancion:
            secciones['seamos_maestros'].append(parte)
        else:
            secciones['vida_cristiana'].append(parte)
    
    return secciones

def determinar_rol(titulo: str) -> str:
    """Determina el rol basado en el título de la parte."""
    titulo_lower = titulo.lower()
    
    if 'lectura' in titulo_lower and 'biblia' in titulo_lower:
        return 'Estudiante:'
    elif any(palabra in titulo_lower for palabra in ['conversación', 'revisita', 'discípulo']):
        return 'Est./Ayud.:'
    elif 'estudio bíblico' in titulo_lower:
        return 'Conductor/Lector:'
    
    return ''

def extraer_datos_reunion(url: str) -> Optional[Dict]:
    """
    Extrae todos los datos de la reunión desde la URL.
    
    Returns:
        Dict con todos los datos estructurados o None si falla
    """
    contenido = obtener_contenido(url)
    if not contenido:
        return None
    
    partes_data = extraer_partes(contenido)
    
    datos = {
        'fecha': extraer_fecha_correcta(contenido),
        'lectura_biblica': extraer_lectura_biblica(contenido),
        'canciones': extraer_canciones(contenido),
        'tesoros_biblia': partes_data['tesoros_biblia'],
        'seamos_maestros': partes_data['seamos_maestros'],
        'vida_cristiana': partes_data['vida_cristiana']
    }
    
    # Debug info
    print(f"  📅 {datos['fecha']}")
    print(f"  📋 Tesoros={len(datos['tesoros_biblia'])}, Maestros={len(datos['seamos_maestros'])}, Vida={len(datos['vida_cristiana'])}")
    
    return datos

# ==================== GENERACIÓN DE HTML ====================

def calcular_horas(partes: List[Dict], hora_inicio: str = "19:06") -> List[Dict]:
    """
    Calcula y asigna horas a cada parte.
    
    Args:
        partes: Lista de partes sin hora
        hora_inicio: Hora de inicio en formato HH:MM
        
    Returns:
        Lista de partes con hora calculada
    """
    h, m = map(int, hora_inicio.split(':'))
    minutos_totales = h * 60 + m
    
    for parte in partes:
        parte['hora'] = f"{minutos_totales // 60:02d}:{minutos_totales % 60:02d}"
        minutos_totales += parte['duracion']
    
    return partes

def generar_html(datos: Dict, congregacion: str = "CONGREGACIÓN CORDIALIDAD") -> str:
    """
    Genera el HTML completo con el formato especificado.
    
    Args:
        datos: Datos extraídos de la reunión
        congregacion: Nombre de la congregación
        
    Returns:
        String con HTML completo
    """
    
    # Calcular horas para cada sección
    tesoros = calcular_horas(datos['tesoros_biblia'].copy(), "19:06")
    maestros = calcular_horas(datos['seamos_maestros'].copy(), "19:30")
    vida = calcular_horas(datos['vida_cristiana'].copy(), "19:47")
    
    # Generar HTML de partes
    def generar_fila(parte: Dict, con_rol: bool = True) -> str:
        if con_rol and parte['rol']:
            return f'''
        <div class="program-row">
            <div class="time">{parte['hora']}</div>
            <div>{parte['numero']}. {parte['titulo']} ({parte['duracion']} min.)</div>
            <div>{parte['rol']}</div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>'''
        else:
            return f'''
        <div class="program-row">
            <div class="time">{parte['hora']}</div>
            <div>{parte['numero']}. {parte['titulo']} ({parte['duracion']} min.)</div>
            <div></div>
            <div></div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>'''
    
    html_tesoros = ''.join(generar_fila(p) for p in tesoros)
    html_maestros = ''.join(generar_fila(p) for p in maestros)
    html_vida = ''.join(generar_fila(p) for p in vida)
    
    # HTML completo (incluyendo el CSS del ejemplo que compartiste)
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programa de reunión - {datos['fecha']}</title>
    <style>
        @page {{ size: letter; margin: 0.5in; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            padding: 10px;
            font-size: 11pt;
            color: #000;
        }}
        .container {{
            max-width: 8.5in;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #0a3ab1, #1e58e7);
            color: white;
            text-align: center;
            padding: 12px;
        }}
        .header h1 {{ margin: 3px 0; font-size: 1.4em; }}
        .header .subtitle {{ font-size: 0.95em; margin-top: 5px; }}
        .info-section {{
            padding: 10px 15px;
            background: #fafafa;
            font-size: 10pt;
        }}
        .info-row {{
            margin: 5px 0;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .info-label {{ 
            font-weight: bold; 
            min-width: 180px; 
        }}
        .name-field {{
            display: inline;
            outline: none;
            color: inherit;
            min-width: 30px;
        }}
        .name-field:empty::before {{
            content: attr(data-placeholder);
            color: #999;
            font-style: italic;
        }}
        .section-header {{
            color: white;
            font-weight: bold;
            padding: 8px 10px;
            font-size: 11pt;
        }}
        .section-header.tesoros {{ background: linear-gradient(135deg, #6c757d, #868e96); }}
        .section-header.maestros {{ background: linear-gradient(135deg, #b8860b, #daa520); }}
        .section-header.vida {{ background: linear-gradient(135deg, #8b0000, #b22222); }}
        .program-row {{
            display: grid;
            grid-template-columns: 60px 1fr 120px 200px 200px;
            font-size: 10pt;
            min-height: 35px;
            padding: 6px 0;
        }}
        .program-row.no-rol {{
            grid-template-columns: 60px 1fr 120px 1fr;
        }}
        .program-row div {{
            padding: 6px 8px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
        }}
        .time {{
            text-align: center;
            font-weight: bold;
            background: #f9f9f9;
            justify-content: center;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; border-radius: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div><strong>{congregacion}</strong></div>
            <h1>Programa para la reunión de entre semana</h1>
            <div class="subtitle">{datos['fecha']} | Lectura: {datos['lectura_biblica']}</div>
        </div>
        
        <div class="info-section">
            <div class="info-row">
                <span class="info-label">Presidente:</span>
                <span contenteditable="true" class="name-field" data-placeholder="Nombre"></span>
            </div>
            <div class="info-row">
                <span class="info-label">Consejero de la sala auxiliar:</span>
                <span contenteditable="true" class="name-field" data-placeholder="Nombre"></span>
            </div>
        </div>
        
        <div class="program-row no-rol">
            <div class="time">19:00</div>
            <div>• Canción {datos['canciones']['inicial']}</div>
            <div></div>
            <div>Oración: <span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>
        <div class="program-row no-rol">
            <div class="time">19:05</div>
            <div>• Palabras de introducción (1 min.)</div>
            <div></div>
            <div></div>
        </div>
        
        <div class="section-header tesoros">TESOROS DE LA BIBLIA</div>
        {html_tesoros}
        
        <div class="section-header maestros">SEAMOS MEJORES MAESTROS</div>
        {html_maestros}
        
        <div class="program-row no-rol">
            <div class="time">19:42</div>
            <div>• Canción {datos['canciones']['intermedia']}</div>
            <div></div>
            <div></div>
        </div>
        
        <div class="section-header vida">NUESTRA VIDA CRISTIANA</div>
        {html_vida}
        
        <div class="program-row no-rol">
            <div class="time">20:32</div>
            <div>• Palabras de conclusión (3 mins.)</div>
            <div></div>
            <div></div>
        </div>
        <div class="program-row no-rol">
            <div class="time">20:35</div>
            <div>• Canción {datos['canciones']['final']}</div>
            <div></div>
            <div>Oración: <span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>
    </div>
</body>
</html>'''

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal: extrae datos y genera HTMLs."""
    print("\n" + "="*70)
    print("🚀 EXTRACTOR DE REUNIONES JW.ORG")
    print("="*70)
    print()
    
    url_indice = input("📎 URL del índice (ej: .../marzo-abril-2026-mwb/): ").strip()
    
    if not url_indice:
        print("❌ URL vacía")
        return
    
    # Obtener enlaces
    enlaces = obtener_enlaces_semanas(url_indice)
    
    if not enlaces:
        print("❌ No se encontraron semanas")
        return
    
    print("\n📅 SEMANAS DISPONIBLES:\n")
    for i, sem in enumerate(enlaces, 1):
        print(f"  {i}. {sem['titulo']}")
    print()
    
    # Procesar todas las semanas
    datos_todas = []
    errores = []
    
    for i, semana in enumerate(enlaces, 1):
        try:
            print(f"⏳ [{i}/{len(enlaces)}] {semana['titulo']}...")
            datos = extraer_datos_reunion(semana['url'])
            
            if datos:
                # Generar HTML individual
                html = generar_html(datos)
                nombre_archivo = f"reunion_{datos['fecha'].replace(' ', '_')}.html"
                
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print(f"  ✅ Generado: {nombre_archivo}\n")
                datos_todas.append(datos)
            else:
                print(f"  ❌ Sin datos\n")
                errores.append(semana['titulo'])
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            errores.append(f"{semana['titulo']}: {e}")
    
    print("="*70)
    print(f"✅ PROCESADAS: {len(datos_todas)}/{len(enlaces)}")
    if errores:
        print(f"❌ ERRORES: {len(errores)}")
        for err in errores:
            print(f"  • {err}")
    print("="*70)

if __name__ == "__main__":
    main()
