# Guía de Configuración: QSAR Toolbox WebAPI + QSAR LLM

Esta guía detalla cómo configurar QSAR Toolbox WebAPI para integración completa con QSAR LLM.

---

## 📋 Tabla de contenidos

1. [Instalación de QSAR Toolbox](#instalación-de-qsar-toolbox)
2. [Activar WebAPI REST](#activar-webapi-rest)
3. [Configurar QSAR LLM](#configurar-qsar-llm)
4. [Validación de conexión](#validación-de-conexión)
5. [Troubleshooting](#troubleshooting)

---

## Instalación de QSAR Toolbox

### Requisitos del sistema
- **Windows** (7+), **Linux** (Ubuntu 16.04+), o **macOS** (10.13+)
- 2+ GB RAM recomendado
- Conexión a internet para descargas iniciales
- Derechos de administrador para instalación

### Descargar e instalar

1. **Descargar QSAR Toolbox v4.8**
   - Ir a: https://www.oecd.org/chemicalsafety/risk-assessment/oecd-qsar-toolbox.htm
   - Click en "Download" (requiere registro gratuito)
   - Seleccionar versión para tu SO

2. **Ejecutar instalador**
   - **Windows**: `QSARToolbox_v4.8_Setup.exe` → Next, Next, Finish
   - **Linux**: `QSARToolbox_v4.8_Linux.tar.gz` → `tar xzf` y seguir instrucciones
   - **macOS**: `QSARToolbox_v4.8_Mac.dmg` → Drag to Applications

3. **Validar instalación**
   ```bash
   # En terminal/cmd, busca QSAR Toolbox en el menú de aplicaciones
   # O ejecuta:
   # Windows: "C:\Program Files\QSAR Toolbox v4.8\QSARToolbox.exe"
   # Linux/Mac: Busca en /opt o /Applications
   ```

---

## Activar WebAPI REST

### Pasos en QSAR Toolbox GUI

1. **Abrir QSAR Toolbox v4.8**
   - Espera a que se cargue completamente (30-60 segundos)
   - Deberías ver la interfaz principal con "Workspace", "Tools", etc.

2. **Ir a Tools → REST API Server**
   ```
   Menu: Tools
   Submenu: REST API Server
   ```
   - O presiona `Ctrl+Alt+R` (Windows/Linux) o `Cmd+Option+R` (macOS)

3. **Activar el servidor**
   - Botón: "START REST API SERVER" (verde)
   - Estado debería cambiar a "API Server Running"
   - Puerto por defecto: **3000**

4. **Verificar en terminal**
   ```bash
   # En terminal/cmd nuevo:
   curl http://localhost:3000/api/v1/version

   # Debería retornar (ejemplo):
   # {"version": "4.8.0", "build": "20231015"}
   ```

### Configuración avanzada (opcional)

Si necesitas cambiar el puerto (por defecto 3000):

**Windows:**
```cmd
# Editar archivo de config
notepad "C:\Program Files\QSAR Toolbox v4.8\config\server.json"
# Cambiar "port": 3000 a lo que desees
# Reiniciar el servidor
```

**Linux/macOS:**
```bash
# Ubicar config
find ~ -name "server.json" -path "*/QSAR*"
# Editar con editor preferido (nano, vim, etc)
nano /path/to/server.json
# Cambiar puerto y guardar
```

---

## Configurar QSAR LLM

### Paso 1: Verificar que QSAR Toolbox está corriendo

Antes de iniciar QSAR LLM, asegúrate que:
- QSAR Toolbox GUI está abierto
- REST API Server muestra "Running"
- `curl http://localhost:3000/api/v1/version` funciona

### Paso 2: Configurar archivo `.env`

En directorio `QSAR LLM/`, edita `.env`:

```env
# Google Gemini API Key (obligatorio)
GEMINI_API_KEY=AIza...tu_key_aqui...

# QSAR Toolbox WebAPI URL
# Si QSAR Toolbox está en puerto por defecto:
TOOLBOX_URL=http://localhost:3000

# Si está en otra máquina o puerto diferente:
# TOOLBOX_URL=http://192.168.1.100:3000
# TOOLBOX_URL=http://qsar-server.example.com:3000

# Puerto del servidor QSAR LLM
PORT=8000

# Modo debug (solo desarrollo)
DEBUG=false

# Opcional: protección de backend
BACKEND_API_KEY=
```

### Paso 3: Iniciar servidor QSAR LLM

```bash
cd "QSAR LLM"
source venv/bin/activate  # En Windows: venv\Scripts\activate
python app.py
```

Output esperado:
```
============================================================
  QSAR LLM — UranoIA Backend
  Puerto: 8000
  QSAR Toolbox URL: http://localhost:3000
  Gemini API: ✓ Configurado
============================================================
 * Running on http://0.0.0.0:8000
```

### Paso 4: Abrir interfaz web

Navega a: **http://localhost:8000**

---

## Validación de conexión

### Mediante interfaz gráfica

1. Click en **⚙️ Configuración** (arriba a la derecha)
2. Verifica valores:
   - URL del servidor QSAR LLM: `http://localhost:8000`
   - API Key de Gemini: `AIza...` (primeros caracteres)
3. Click en **🔍 Diagnosticar**
4. Deberías ver:
   ```
   ✓ Backend disponible en http://localhost:8000
     → Versión QSAR Toolbox: 4.8
   ✓ QSAR Toolbox WebAPI conectado
   ✓ Health check completado
     → Status: healthy
     ✓ Conectividad OK
     ✓ Profilers disponibles
     ✓ Search de sustancias OK
   ✓ PubChem lookup disponible
   ✓ API Key de Gemini detectada
   ```

### Mediante terminal

```bash
# Verificar backend
curl http://localhost:8000/api/status
# Debería retornar JSON con "toolbox_connected": true

# Verificar health de QSAR Toolbox
curl http://localhost:8000/api/toolbox/health
# Debería retornar status: "healthy"

# Buscar sustancia (test)
curl http://localhost:8000/api/toolbox/search?q=1071-83-6
# Debería retornar datos del glifosato si Toolbox está conectado
```

---

## Troubleshooting

### ❌ "QSAR Toolbox WebAPI no disponible"

**Causa 1: QSAR Toolbox no está abierto**
```bash
# Solución: Abre QSAR Toolbox y mantén abierto mientras usas QSAR LLM
# El REST API Server debe mostrar "Running" en la GUI
```

**Causa 2: Puerto 3000 bloqueado/en uso**
```bash
# Verificar qué está usando puerto 3000:
# Windows: netstat -ano | findstr :3000
# Linux/Mac: lsof -i :3000

# Solución: Cambiar puerto en QSAR Toolbox server.json
# O usar TOOLBOX_URL diferente en .env
```

**Causa 3: Firewall bloquea localhost:3000**
```bash
# Solución: Permitir conexiones en firewall
# Windows: Agregar excepción para QSAR Toolbox
# Linux: sudo ufw allow 3000
# Mac: System Preferences → Security → permitir QSAR Toolbox
```

### ❌ Timeout o conexión lenta

**Solución:**
- Aumentar timeout en request (por defecto 60s)
- Verificar que QSAR Toolbox no está bajo carga pesada
- Reiniciar QSAR Toolbox y servidor QSAR LLM

```bash
# En QSAR Toolbox, verificar recursos:
# Abrir Task Manager → buscar java.exe o QSARToolbox
# Debería usar <500MB RAM si está idle
```

### ✓ La app funciona pero sin datos de Toolbox

**Es normal:** Si QSAR Toolbox no está disponible, QSAR LLM:
- Funciona en modo demo
- Usa PubChem para datos químicos
- Proporciona análisis regulatorio mediante Gemini AI
- No pueden acceder a perfilado estructural ni read-across

**Solución:** Conectar QSAR Toolbox según pasos anteriores

---

## Ejemplos de uso

### Ejemplo 1: Análisis simple de moléculas

```bash
# Terminal 1: Ejecuta QSAR Toolbox GUI
# (Abre desde aplicaciones)

# Terminal 2: Ejecuta servidor QSAR LLM
cd "QSAR LLM"
python app.py

# Terminal 3: Prueba endpoint (o usa interfaz web)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analiza glifosato CAS 1071-83-6",
    "options": {
      "profiling": true,
      "readAcross": true,
      "mutagen": true
    },
    "language": "es"
  }'
```

### Ejemplo 2: Perfilado estructural directo

```bash
curl -X POST http://localhost:8000/api/toolbox/profile \
  -H "Content-Type: application/json" \
  -d '{
    "cas": "1071-83-6",
    "profilers": ["mutagenicity", "aquatic_toxicity", "skin_sensitization"]
  }'
```

### Ejemplo 3: Construcción de categoría

```bash
curl -X POST http://localhost:8000/api/toolbox/category \
  -H "Content-Type: application/json" \
  -d '{
    "cas": "1071-83-6"
  }'
```

---

## Recursos adicionales

- **Documentación OECD QSAR Toolbox**: https://www.oecd.org/chemicalsafety/risk-assessment/oecd-qsar-toolbox.htm
- **OECD TG 497** (Skin sensitization): https://www.oecd.org/publication/TG497
- **REACH Annex XI** (QSAR criteria): https://echa.europa.eu/documents/10162/13632/qsar_guidance_en.pdf
- **QSAR LLM GitHub**: https://github.com/cvrussu/qsar-llm

---

## Soporte

Si encuentras problemas:

1. **Verifica logs** de QSAR Toolbox (usualmente en `%APPDATA%\QSAR Toolbox\logs`)
2. **Revisa consola** de QSAR LLM para mensajes de error
3. **Corre diagnóstico** mediante 🔍 en la interfaz
4. **Contacta a UranoIA**: https://uranoia.cl

