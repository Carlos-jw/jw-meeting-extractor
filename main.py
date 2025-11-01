"""
JW Meeting Program Extractor
Extractor de Programas de Reunión de JW.org

Versión: 1.0.0
Puerto: 5000
"""

from flask import Flask
from flask_cors import CORS
from routes import init_routes
import os

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jw-extractor-secret-key-2025')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['JSON_AS_ASCII'] = False
    
    # Habilitar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Crear directorios necesarios
    os.makedirs('output', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Inicializar rutas
    init_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("🎯 JW MEETING PROGRAM EXTRACTOR")
    print("="*60)
    print("✅ Servidor iniciado correctamente")
    print("📍 URL: http://localhost:5000")
    print("🔧 Modo: Desarrollo")
    print("📁 Carpeta output: ./output/")
    print("="*60 + "\n")
    
    # Para Replit y producción
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
