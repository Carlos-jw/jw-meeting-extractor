# 📋 JW Meeting Program Extractor

Extractor automatizado de programas de reunión de JW.org con generación de plantillas HTML editables.

[![Run on Replit](https://replit.com/badge/github/TUUSUARIO/jw-meeting-extractor)](https://replit.com/github/TUUSUARIO/jw-meeting-extractor)

> ⚠️ **IMPORTANTE:** Reemplaza `TUUSUARIO` en el badge arriba con tu usuario de GitHub

---

## 🎯 Características

✅ Búsqueda automática de semanas disponibles en JW.org  
✅ Extracción inteligente de datos estructurados  
✅ Plantillas HTML editables listas para imprimir  
✅ Extracción individual o masiva  
✅ Exportación a PDF o imagen desde la plantilla  
✅ Interfaz web moderna y fácil de usar  

---

## 🚀 Uso Rápido en Replit

### Método 1: Click en el badge (arriba)

1. Click en "Run on Replit"
2. Espera a que se instalen dependencias
3. La app se ejecutará automáticamente
4. ¡Listo! 🎉

### Método 2: Importar manualmente

1. Ve a [replit.com](https://replit.com)
2. Click "Import from GitHub"
3. Pega la URL de este repo
4. Click "Import"
5. Click "Run"

---

## 📖 Cómo Usar

1. **Ingresar URL del índice de JW.org**
   - Ejemplo: `https://www.jw.org/es/biblioteca/guia-actividades-reunion-testigos-jehova/`

2. **Ingresar nombre de congregación**
   - Ejemplo: `CONGREGACIÓN CENTRO`

3. **Buscar semanas disponibles**
   - Click en "🔍 Buscar Semanas"

4. **Extraer semana**
   - Click en "📥 Extraer" en la semana deseada

5. **Descargar plantilla HTML**
   - Click en "💾 Descargar Plantilla"
   - Abrir archivo en navegador
   - Rellenar nombres
   - Imprimir PDF o guardar imagen

---

## 📁 Estructura
```
jw-meeting-extractor/
├── main.py                    # Servidor Flask
├── routes.py                  # Endpoints API
├── utils/
│   ├── jw_scraper.py         # Scraper JW.org
│   └── template_generator.py # Generador HTML
├── templates/
│   └── index.html            # Frontend
├── output/                    # Plantillas generadas
└── requirements.txt
```

---

## 🔧 Instalación Local
```bash
# Clonar
git clone https://github.com/TUUSUARIO/jw-meeting-extractor.git
cd jw-meeting-extractor

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py

# Abrir navegador
http://localhost:5000
```

---

## 📝 Notas

⚠️ Este proyecto es para uso personal/congregacional  
⚠️ Respeta los términos de uso de JW.org  
⚠️ No hace modificaciones a JW.org, solo extrae información pública  

---

## 📜 Licencia

MIT License - Uso libre para fines educativos y congregacionales

---

**¡Hecho con ❤️ para facilitar el trabajo de las congregaciones!**
