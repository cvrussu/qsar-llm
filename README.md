# QSAR LLM — UranoIA
**Agente de evaluación regulatoria de agroquímicos con IA**

Versión: `1.0.0-beta` | Autor: Claudio Valdés Russu | UranoIA · Villarrica, Chile

---

## ¿Qué es QSAR LLM?

QSAR LLM es una interfaz conversacional que combina el **OECD QSAR Toolbox v4.8** con **Claude AI (Anthropic)** para asistir a consultores y expertos regulatorios en la evaluación toxicológica in silico de agroquímicos.

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
- Python 3.10+
- OECD QSAR Toolbox v4.8 instalado (Windows/Linux)
- Cuenta Anthropic con API key

### Pasos

```bash
# 1. Entrar al directorio
cd "QSAR LLM"

# 2. Dar permisos al script de inicio (macOS/Linux)
chmod +x start.sh

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key de Anthropic

# 4. Iniciar
./start.sh
```

En Windows:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
:: Editar .env
python app.py
```

### Abrir la interfaz
Navega a: **http://localhost:5000**

---

## Configuración del QSAR Toolbox

El QSAR Toolbox incluye una API REST desde la versión 4.7. Para activarla:

1. Abrir QSAR Toolbox 4.8
2. Ir a **Tools → REST API Server**
3. Activar en el puerto por defecto (3000)
4. Asegurarse de que `TOOLBOX_URL=http://localhost:3000` en `.env`

Si el Toolbox no está disponible, la app funciona en **modo demo** con datos de PubChem + análisis LLM.

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
| `ANTHROPIC_API_KEY` | API key de Anthropic | Sí |
| `TOOLBOX_URL` | URL del QSAR Toolbox local | No (default: localhost:3000) |
| `PORT` | Puerto del servidor Flask | No (default: 5000) |
| `DEBUG` | Modo debug | No (default: false) |
| `BACKEND_API_KEY` | Protección opcional del backend | No |

---

## Endpoints de la API

| Endpoint | Método | Descripción |
|---|---|---|
| `GET /api/status` | GET | Estado del servidor y Toolbox |
| `POST /api/chat` | POST | Chat principal (LLM + Toolbox) |
| `GET /api/toolbox/search?q=CAS` | GET | Búsqueda en Toolbox |
| `POST /api/toolbox/profile` | POST | Perfilado estructural |
| `POST /api/toolbox/category` | POST | Construcción de categoría |
| `GET /api/pubchem?q=CAS` | GET | Datos PubChem |

### Ejemplo de request al chat:
```json
POST /api/chat
{
  "query": "Analiza el glifosato CAS 1071-83-6",
  "options": {
    "profiling": true,
    "readAcross": true,
    "aquatic": true,
    "mutagen": true
  },
  "model": "claude-sonnet-4-6",
  "language": "es"
}
```

---

## Disclaimer regulatorio

> Las predicciones in silico generadas por QSAR LLM son herramientas de **apoyo científico** y no reemplazan ensayos experimentales certificados GLP. Su uso debe enmarcarse dentro de las guías OCDE y los requisitos regulatorios aplicables. UranoIA no asume responsabilidad por decisiones regulatorias basadas exclusivamente en estos resultados.

---

## Licencia y créditos

- **OECD QSAR Toolbox**: © OCDE/ECHA/LMC — Software gratuito, uso regulatorio
- **Claude AI**: © Anthropic — API comercial
- **QSAR LLM**: © 2025 UranoIA / Claudio Valdés Russu

Para soporte y consultoría: [UranoIA](https://uranoia.cl)
