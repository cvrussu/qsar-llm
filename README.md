# QSAR LLM — UranoIA
**Agente de evaluación regulatoria de agroquímicos con IA**

Versión: `1.0.0-beta` | Autor: Claudio Valdés Russu | UranoIA · Villarrica, Chile

---

## ¿Qué es QSAR LLM?

QSAR LLM es una interfaz conversacional que combina el **OECD QSAR Toolbox v4.8** con **Google Gemini AI** para asistir a consultores y expertos regulatorios en la evaluación toxicológica in silico de agroquímicos.

El usuario puede ingresar un **número CAS**, **nombre de molécula** o **SMILES** y recibir un análisis regulatorio completo que incluye:

- Perfilado estructural (73 esquemas del QSAR Toolbox)
- Predicciones de toxicidad acuática (CL50, NOEC)
- Genotoxicidad / Test de Ames in silico
- Read-across y construcción de categorías químicas
- Análisis de sensibilización cutánea (DASSAW, OECD TG 497)
- Rutas metabólicas y metabolitos relevantes
- Contexto regulatorio (REACH, Reg. 1107/2009, ANVISA, EPA)

---

## Instalación rápida

### Requisitos
- Python 3.9+ (incluye 3.10, 3.11, 3.12)
- OECD QSAR Toolbox v4.8 instalado (Windows/Linux) — *opcional pero recomendado*
- API key de Google Gemini (gratuita desde [Google AI Studio](https://aistudio.google.com/app/apikey))

### Pasos

```bash
# 1. Entrar al directorio
cd "QSAR LLM"

# 2. Dar permisos al script de inicio (macOS/Linux)
chmod +x start.sh

# 3. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key de Google Gemini

# 5. Iniciar servidor
python app.py
# O con el script proporcionado:
chmod +x start.sh && ./start.sh
```

### Abrir la interfaz
Navega a: **http://localhost:8000** (o el puerto que hayas configurado)

### Validación rápida
Una vez que el servidor esté corriendo, puedes hacer clic en el botón **🔍 Diagnosticar** en las ⚙️ Configuración para verificar que todo está conectado correctamente.

---

## Configuración del QSAR Toolbox WebAPI

### ⚡ Modo sin QSAR Toolbox (Demo)
Si no tienes QSAR Toolbox instalado, la app funciona completamente en **modo demo** usando:
- PubChem API para datos químicos
- Google Gemini para análisis regulatorio contextualizado
- Respuestas informativas basadas en IA sin análisis estructurales profundos

### 🔬 Modo con QSAR Toolbox (Recomendado)
Para acceso a perfilado estructural completo y read-across, activa QSAR Toolbox WebAPI:

**Pasos:**
1. **Instalar QSAR Toolbox v4.8** desde [OECD/ECHA](https://www.oecd.org/chemicalsafety/risk-assessment/oecd-qsar-toolbox.htm)
2. **Abrir QSAR Toolbox** → **Tools → REST API Server** → **Activar**
3. Verificar que corre en puerto 3000 (por defecto: `http://localhost:3000`)
4. En `.env` asegurarse: `TOOLBOX_URL=http://localhost:3000`
5. Reiniciar servidor QSAR LLM

**Verificar conexión:**
- Click en ⚙️ Configuración → 🔍 **Diagnosticar**
- Debe mostrar: `✓ QSAR Toolbox WebAPI conectado`

### Endpoints QSAR Toolbox WebAPI
La app usa los siguientes endpoints de QSAR Toolbox:
- `GET /api/v1/version` — Versión del software
- `GET /api/v1/substances/search` — Búsqueda de sustancias
- `POST /api/v1/profiling/run` — Perfilado estructural
- `POST /api/v1/category/build` — Construcción de categorías
- `POST /api/v1/category/datamatrix` — Matriz de datos
- `POST /api/v1/readacross/predict` — Predicciones read-across

---

## Estructura del proyecto

```
QSAR LLM/
├── index.html       ← Interfaz web completa (frontend)
├── app.py           ← Backend Flask (API)
├── requirements.txt ← Dependencias Python
├── .env.example     ← Plantilla de variables de entorno
├── .env             ← Variables de entorno (NO compartir)
├── start.sh         ← Script de inicio (macOS/Linux)
└── README.md        ← Este archivo
```

---

## Variables de entorno

| Variable | Descripción | Obligatorio |
|---|---|---|
| `GEMINI_API_KEY` | API key de Google Gemini | **Sí** |
| `TOOLBOX_URL` | URL del QSAR Toolbox WebAPI | No (default: `http://localhost:3000`) |
| `PORT` | Puerto del servidor Flask | No (default: `5000`, en ejemplos usamos `5001` o `8000`) |
| `DEBUG` | Modo debug (true/false) | No (default: `false`) |
| `BACKEND_API_KEY` | Protección opcional del backend | No |

**Obtener API key de Gemini:**
1. Ir a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click en "Get API key"
3. Click en "Create API key in new project"
4. Copiar el key y pegarlo en `.env`

---

## Endpoints de la API

### Status & Diagnostics
| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/status` | GET | Estado del servidor y Toolbox |
| `GET /api/toolbox/health` | GET | Diagnóstico detallado QSAR Toolbox |

### Chat & Analysis
| Endpoint | Método | Descripción |
|---|---|---|
| `POST /api/chat` | POST | Chat principal (Gemini + Toolbox + PubChem) |

### QSAR Toolbox Proxy
| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/toolbox/search?q=CAS` | GET | Búsqueda de sustancia por CAS/nombre |
| `GET /api/toolbox/substances/<id>` | GET | Detalles de sustancia |
| `GET /api/toolbox/profilers` | GET | Profilers disponibles |
| `POST /api/toolbox/profile` | POST | Ejecutar perfilado estructural |
| `POST /api/toolbox/category` | POST | Construir categoría química |
| `POST /api/toolbox/datamatrix` | POST | Generar matriz de datos |
| `POST /api/toolbox/readacross` | POST | Predicción read-across |

### PubChem & External Data
| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/pubchem?q=CAS` | GET | Datos químicos desde PubChem |

### Ejemplo de request al chat:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analiza el glifosato CAS 1071-83-6",
    "options": {
      "profiling": true,
      "readAcross": true,
      "aquatic": true,
      "mutagen": true
    },
    "language": "es"
  }'
```

### Ejemplo de diagnóstico:
```bash
curl http://localhost:8000/api/toolbox/health
```

---

## Disclaimer regulatorio

> Las predicciones in silico generadas por QSAR LLM son herramientas de **apoyo científico** y no reemplazan ensayos experimentales certificados GLP. Su uso debe enmarcarse dentro de las guías OCDE y los requisitos regulatorios aplicables. UranoIA no asume responsabilidad por decisiones regulatorias basadas exclusivamente en estos resultados.

---

## Troubleshooting

**Problema: "API desconectada · Modo demo"**
- Verifica que el servidor Flask está ejecutándose en el puerto correcto
- Asegúrate que `apiUrl` en configuración apunta a la URL correcta
- Intenta el botón 🔍 **Diagnosticar** para más detalles

**Problema: "QSAR Toolbox WebAPI no disponible"**
- Verifica que QSAR Toolbox está instalado y el REST API Server está activado
- Confirma que está escuchando en puerto 3000 (u otro configurado)
- Comprueba que el firewall no bloquea conexiones localhost:3000

**Problema: Respuestas genéricas de Gemini (sin datos del Toolbox)**
- Es normal si QSAR Toolbox no está disponible — la app funciona en modo demo
- Las respuestas serán basadas en IA pero sin análisis estructurales
- Conecta QSAR Toolbox para análisis completos

**Problema: Timeout en /api/chat**
- Puede ocurrir si QSAR Toolbox está lento
- Verifica salud del Toolbox con 🔍 **Diagnosticar**
- Aumenta el timeout en cliente (por defecto 60s)

---

## Licencia y créditos

- **OECD QSAR Toolbox v4.8**: © OCDE/ECHA/LMC — Software gratuito, uso regulatorio
- **Google Gemini AI**: © Google — API comercial (tier gratuito disponible)
- **QSAR LLM**: © 2025 UranoIA / Claudio Valdés Russu

Para soporte y consultoría: [UranoIA](https://uranoia.cl)

---

## Roadmap futuro

- [ ] Soporte para moléculas dibujadas (canvas SMILES)
- [ ] Exportación a IUCLID6 y eChem Portal
- [ ] Caché de resultados QSAR Toolbox
- [ ] API de autenticación y multi-usuario
- [ ] Dashboard de historial de análisis
- [ ] Integración con bases de datos regulatorias (ECHA, EPA)
- [ ] Análisis de metabolitos y rutas de transformación
- [ ] Generación automática de reportes PDF REACH-compliant
