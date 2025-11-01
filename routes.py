"""
Routes module - Endpoints de la API
"""

from flask import render_template, request, jsonify, send_file
from utils.jw_scraper import extraer_indice_semanas, extraer_datos_semana
from utils.template_generator import generar_plantilla_editable
import os
import json
from datetime import datetime

# Almacenamiento temporal de datos extraídos
datos_extraidos = {}

def init_routes(app):
    """Inicializa todas las rutas de la aplicación"""
    
    @app.route('/')
    def index():
        """Página principal"""
        return render_template('index.html')
    
    @app.route('/api/semanas', methods=['POST'])
    def buscar_semanas():
        """Busca todas las semanas disponibles en el índice de JW.org"""
        try:
            data = request.get_json()
            url = data.get('url', '').strip()
            
            if not url:
                return jsonify({'success': False, 'error': 'URL no proporcionada'}), 400
            
            if not url.startswith('https://www.jw.org'):
                return jsonify({'success': False, 'error': 'URL debe ser de jw.org'}), 400
            
            print(f"\n🔍 Buscando semanas en: {url}")
            
            semanas = extraer_indice_semanas(url)
            
            if not semanas:
                return jsonify({
                    'success': False,
                    'error': 'No se encontraron semanas en la URL proporcionada'
                }), 404
            
            print(f"✅ Se encontraron {len(semanas)} semanas")
            
            return jsonify({
                'success': True,
                'total': len(semanas),
                'semanas': semanas
            })
            
        except Exception as e:
            print(f"❌ Error al buscar semanas: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error al procesar la solicitud: {str(e)}'
            }), 500
    
    @app.route('/api/extraer', methods=['POST'])
    def extraer_semana():
        """Extrae datos estructurados de una semana específica"""
        try:
            data = request.get_json()
            url = data.get('url', '').strip()
            
            if not url:
                return jsonify({'success': False, 'error': 'URL no proporcionada'}), 400
            
            print(f"\n📥 Extrayendo datos de: {url}")
            
            datos = extraer_datos_semana(url)
            
            if not datos or 'error' in datos:
                error_msg = datos.get('error', 'Error desconocido') if datos else 'No se pudieron extraer datos'
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            
            semana_id = generar_id_semana(datos['fecha'])
            
            datos_extraidos[semana_id] = {
                'datos': datos,
                'fecha_extraccion': datetime.now().isoformat(),
                'url': url
            }
            
            print(f"✅ Datos extraídos correctamente: {datos['fecha']}")
            
            return jsonify({
                'success': True,
                'semana_id': semana_id,
                'datos': datos
            })
            
        except Exception as e:
            print(f"❌ Error al extraer semana: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error al extraer datos: {str(e)}'
            }), 500
    
    @app.route('/api/extraer-multiples', methods=['POST'])
    def extraer_multiples():
        """Extrae múltiples semanas de forma secuencial"""
        try:
            data = request.get_json()
            urls = data.get('urls', [])
            
            if not urls:
                return jsonify({'success': False, 'error': 'No se proporcionaron URLs'}), 400
            
            print(f"\n📦 Extrayendo {len(urls)} semanas...")
            
            resultados = []
            exitosos = 0
            fallidos = 0
            
            for i, url in enumerate(urls, 1):
                print(f"  [{i}/{len(urls)}] Procesando...")
                
                try:
                    datos = extraer_datos_semana(url)
                    
                    if datos and 'error' not in datos:
                        semana_id = generar_id_semana(datos['fecha'])
                        datos_extraidos[semana_id] = {
                            'datos': datos,
                            'fecha_extraccion': datetime.now().isoformat(),
                            'url': url
                        }
                        
                        resultados.append({
                            'success': True,
                            'semana_id': semana_id,
                            'titulo': datos['fecha'],
                            'url': url
                        })
                        exitosos += 1
                        print(f"  ✅ {datos['fecha']}")
                    else:
                        resultados.append({
                            'success': False,
                            'error': datos.get('error', 'Error desconocido'),
                            'url': url
                        })
                        fallidos += 1
                        print(f"  ❌ Error")
                        
                except Exception as e:
                    resultados.append({
                        'success': False,
                        'error': str(e),
                        'url': url
                    })
                    fallidos += 1
                    print(f"  ❌ {str(e)}")
            
            print(f"\n✅ Extracción masiva completada: {exitosos} exitosos, {fallidos} fallidos")
            
            return jsonify({
                'success': True,
                'total': len(urls),
                'exitosos': exitosos,
                'fallidos': fallidos,
                'resultados': resultados
            })
            
        except Exception as e:
            print(f"❌ Error en extracción masiva: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error al extraer múltiples semanas: {str(e)}'
            }), 500
    
    @app.route('/api/descargar-plantilla/<semana_id>')
    def descargar_plantilla(semana_id):
        """Descarga la plantilla HTML editable de una semana"""
        try:
            if semana_id not in datos_extraidos:
                return jsonify({'error': 'Semana no encontrada. Extrae los datos primero.'}), 404
            
            datos = datos_extraidos[semana_id]['datos']
            nombre_congregacion = request.args.get('congregacion', 'CONGREGACIÓN')
            
            print(f"\n💾 Generando plantilla para: {datos['fecha']}")
            
            html_content = generar_plantilla_editable(datos, nombre_congregacion)
            
            filename = f"programa-{semana_id}.html"
            filepath = os.path.join('output', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Plantilla guardada: {filepath}")
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='text/html'
            )
            
        except Exception as e:
            print(f"❌ Error al descargar plantilla: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/datos/<semana_id>')
    def obtener_datos(semana_id):
        """Obtiene los datos JSON de una semana extraída"""
        if semana_id not in datos_extraidos:
            return jsonify({'error': 'Semana no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'datos': datos_extraidos[semana_id]
        })
    
    @app.route('/api/salud')
    def salud():
        """Endpoint de health check"""
        return jsonify({
            'status': 'ok',
            'servicio': 'JW Meeting Extractor',
            'version': '1.0.0',
            'semanas_en_memoria': len(datos_extraidos)
        })

def generar_id_semana(fecha):
    """Genera un ID único basado en la fecha"""
    return fecha.lower().replace(' de ', '-').replace(' ', '-')
