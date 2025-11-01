"""
Template Generator
Genera plantillas HTML editables para programas de reunión
"""

from typing import Dict, List

def generar_plantilla_editable(datos: Dict, nombre_congregacion: str = "CONGREGACIÓN") -> str:
    """
    Genera HTML editable completo
    
    Args:
        datos: Diccionario con datos extraídos de la semana
        nombre_congregacion: Nombre de la congregación
        
    Returns:
        String con HTML completo
    """
    
    fecha = datos.get('fecha', 'Fecha no disponible')
    lectura = datos.get('lectura_biblica', 'N/A')
    cancion_inicial = datos.get('cancion_inicial', 'N/A')
    cancion_intermedia = datos.get('cancion_intermedia', 'N/A')
    cancion_final = datos.get('cancion_final', 'N/A')
    
    tesoros = datos.get('tesoros_biblia', [])
    maestros = datos.get('seamos_maestros', [])
    vida = datos.get('vida_cristiana', [])
    
    filename = fecha.lower().replace(' de ', '-').replace(' ', '-')
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programa de reunión - {fecha}</title>
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
            text-align: left;
        }}
        .name-field {{
            display: inline;
            outline: none;
            color: inherit;
            font-family: inherit;
            font-size: inherit;
            padding: 0;
            margin: 0;
            background: transparent;
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
        .section-header.tesoros {{ 
            background: linear-gradient(135deg, #6c757d, #868e96); 
        }}
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
        .program-row:not(.no-rol) div:nth-child(4),
        .program-row:not(.no-rol) div:nth-child(5) {{
            justify-content: center;
            text-align: center;
        }}
        .program-row.no-rol div:nth-child(4) {{
            justify-content: flex-end;
            text-align: right;
            padding-right: 12px;
        }}
        .time {{
            text-align: center;
            font-weight: bold;
            background: #f9f9f9;
            justify-content: center;
        }}
        
        .print-buttons {{
            display: flex;
            gap: 10px;
            justify-content: center;
            padding: 15px;
            background: #f0f0f0;
            border-top: 2px solid #ddd;
        }}
        .btn-print {{
            padding: 10px 20px;
            font-size: 11pt;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-pdf {{
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
        }}
        .btn-pdf:hover {{
            background: linear-gradient(135deg, #c82333, #bd2130);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .btn-image {{
            background: linear-gradient(135deg, #28a745, #218838);
            color: white;
        }}
        .btn-image:hover {{
            background: linear-gradient(135deg, #218838, #1e7e34);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        @media print {{
            body {{ background: white; padding: 0; color: black; }}
            .container {{ 
                box-shadow: none; 
                border-radius: 0; 
                max-width: 8.5in; 
                width: 8.5in;
            }}
            .name-field {{
                color: black;
                background: transparent;
            }}
            .name-field:empty::before {{ content: ""; }}
            .print-buttons {{ display: none; }}
        }}
        
        @media (max-width: 600px) {{
            .container {{
                max-width: 100%;
                border-radius: 0;
            }}
            body {{ padding: 8px; font-size: 9pt; }}
            .header h1 {{ font-size: 1.2em; }}
            .program-row,
            .program-row.no-rol {{
                display: block;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .program-row div {{
                display: block;
                padding: 4px 0;
            }}
            .time {{
                background: #f0f0f0;
                text-align: center;
                font-weight: bold;
                padding: 6px 0;
                margin-bottom: 6px;
                border-radius: 4px;
            }}
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div><strong>{nombre_congregacion.upper()}</strong></div>
            <h1>Programa para la reunión de entre semana</h1>
            <div class="subtitle">{fecha} | Lectura: {lectura}</div>
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
            <div>• Canción {cancion_inicial}</div>
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
'''
    
    for parte in tesoros:
        html += generar_fila_parte(parte)
    
    html += '''
        <div class="section-header maestros">SEAMOS MEJORES MAESTROS</div>
'''
    
    for parte in maestros:
        html += generar_fila_parte(parte)
    
    html += f'''
        <div class="section-header vida">NUESTRA VIDA CRISTIANA</div>
        <div class="program-row no-rol">
            <div class="time">{calcular_hora_cancion_intermedia(tesoros, maestros)}</div>
            <div>• Canción {cancion_intermedia}</div>
            <div></div>
            <div></div>
        </div>
'''
    
    for parte in vida:
        html += generar_fila_parte(parte)
    
    html += f'''
        <div class="program-row no-rol">
            <div class="time">{calcular_hora_final(tesoros, maestros, vida)}</div>
            <div>• Palabras de conclusión (3 mins.)</div>
            <div></div>
            <div></div>
        </div>
        <div class="program-row no-rol">
            <div class="time">{calcular_hora_final(tesoros, maestros, vida, extra=3)}</div>
            <div>• Canción {cancion_final}</div>
            <div></div>
            <div>Oración: <span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>
        
        <div class="print-buttons">
            <button class="btn-print btn-pdf" onclick="imprimirPDF()">
                <span>📄</span> Imprimir como PDF
            </button>
            <button class="btn-print btn-image" onclick="guardarImagen()">
                <span>🖼️</span> Guardar como Imagen
            </button>
        </div>
    </div>
    
    <script>
        function imprimirPDF() {{
            window.print();
        }}
        
        async function guardarImagen() {{
            const container = document.querySelector('.container');
            const buttons = document.querySelector('.print-buttons');
            
            buttons.style.display = 'none';
            
            try {{
                const canvas = await html2canvas(container, {{
                    scale: 2,
                    backgroundColor: '#ffffff',
                    logging: false,
                    useCORS: true
                }});
                
                const link = document.createElement('a');
                link.download = 'programa-reunion-{filename}.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }} catch (error) {{
                alert('Error al generar la imagen.');
                console.error(error);
            }} finally {{
                buttons.style.display = 'flex';
            }}
        }}
    </script>
</body>
</html>'''
    
    return html

def generar_fila_parte(parte: Dict) -> str:
    """Genera una fila HTML para una parte del programa"""
    hora = parte.get('hora', '00:00')
    titulo = parte.get('titulo', 'Sin título')
    duracion = parte.get('duracion', '0')
    rol = parte.get('rol')
    numero = parte.get('numero', '')
    
    if rol:
        return f'''
        <div class="program-row">
            <div class="time">{hora}</div>
            <div>{numero}. {titulo} ({duracion} mins.)</div>
            <div>{rol}</div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>
'''
    else:
        return f'''
        <div class="program-row">
            <div class="time">{hora}</div>
            <div>{numero}. {titulo} ({duracion} mins.)</div>
            <div></div>
            <div></div>
            <div><span contenteditable="true" class="name-field" data-placeholder="Nombre"></span></div>
        </div>
'''

def calcular_hora_cancion_intermedia(tesoros: List, maestros: List) -> str:
    """Calcula hora de canción intermedia"""
    minutos = 19 * 60 + 6
    
    for parte in tesoros:
        minutos += int(parte.get('duracion', 0))
    for parte in maestros:
        minutos += int(parte.get('duracion', 0))
    
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

def calcular_hora_final(tesoros: List, maestros: List, vida: List, extra: int = 0) -> str:
    """Calcula hora final"""
    minutos = 19 * 60 + 6
    
    for parte in tesoros:
        minutos += int(parte.get('duracion', 0))
    for parte in maestros:
        minutos += int(parte.get('duracion', 0))
    for parte in vida:
        minutos += int(parte.get('duracion', 0))
    
    minutos += extra
    
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"
