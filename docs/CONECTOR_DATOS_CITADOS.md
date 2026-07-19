# Conector de datos toxicológicos con citación — Diseño de arquitectura

**Objetivo:** permitir consultas del tipo *"búscame los datos de irritación dérmica de abamectina"* y devolver el valor/clasificación **con su fuente citada**, sin que el LLM invente referencias.

Proyecto: QSAR LLM — UranoIA · Estado: **diseño / documentación** (no implementado aún)
Última actualización: 2026-07-19

---

## 1. Principio de diseño: RAG con procedencia

El requisito *"que me lo cite"* **no** se resuelve pidiéndole a Gemini que recuerde datos — eso produce citas inventadas. Se resuelve así:

```
Usuario → (1) RESOLVER identidad química → (2) RECUPERAR registros estructurados
        de APIs regulatorias (cada registro YA trae su fuente)
        → (3) Gemini SOLO formatea/traduce, citando la fuente devuelta por la API
```

> **Regla de oro:** el LLM nunca es la fuente del dato ni de la cita. La fuente es el registro estructurado de la API. Gemini es la capa de presentación.

---

## 2. Fuentes conectables (APIs reales)

### 2.1 OECD QSAR Toolbox WebAPI ⭐ (ya integrado en `app.py`)
- **Base:** `http://localhost:3000/api/v1` (config `TOOLBOX_URL`)
- **Cobertura dérmica:** bases de datos *Skin irritation/corrosion* (ECHA, OASIS, etc.)
- **Cómo citar:** el `datamatrix` devuelve valores experimentales **con la referencia del estudio/DB de origen**.
- **Endpoints relevantes (ya proxeados):**
  - `GET /substances/search?q={CAS}` → resuelve la sustancia
  - `POST /category/datamatrix` → matriz de datos experimentales (incluye endpoints como irritación dérmica **con fuente**)
- **A confirmar contra el Swagger de tu v4.8** (`/api/v1/` → docs): si existe un endpoint directo de *data gathering* por sustancia+endpoint, es preferible al `datamatrix`.

### 2.2 EPA CompTox / CCTE APIs — ToxValDB "Hazard" (recomendado como fallback fuerte)
- **Base:** `https://api-ccte.epa.gov`
- **Auth:** API key gratuita (solicitar a `ccte_api@epa.gov`), header `x-api-key`
- **Cobertura dérmica:** ToxValDB incluye registros **skin-eye irritation**, con referencia de estudio/fuente
- **Flujo:**
  1. Resolver identidad → `GET /chemical/search/equal/{nombre-o-CAS}` → obtiene **DTXSID**
  2. Recuperar peligro → endpoints de la *Hazard API* por DTXSID (skin-eye irritation)
- **Docs:** https://comptox.epa.gov/ctx-api/docs/chemical.html · Clientes: `USEPA/ccte-api-hazard` (GitHub), paquete R `ctxR`

### 2.3 PubChem PUG-REST / PUG-View (fallback público, sin API key)
- **Base:** `https://pubchem.ncbi.nlm.nih.gov/rest`
- **Cobertura dérmica:** clasificación **GHS** (Skin Irrit./Skin Corr.) con atribución de fuente (ECHA C&L, etc.)
- **Flujo:**
  1. `GET /pug/compound/name/{nombre}/cids/JSON` → CID
  2. `GET /pug_view/data/compound/{CID}/JSON?heading=GHS+Classification` → categorías GHS + fuente
- **Nota:** ya lo usas en modo demo; sin gestión de keys.

### 2.4 eChemPortal (OECD) — cross-dossier (sin REST oficial)
- **Portal:** https://www.echemportal.org/ (búsqueda por sustancia / propiedad / GHS)
- **Uso:** enlazar al **dossier regulatorio** original (ECHA/EPA) como cita de respaldo
- **Acceso programático:** no hay API pública oficial; existe scraper comunitario `biobricks-ai/echemportal`. Mejor como enlace de verificación humana que como fuente automatizada.

### 2.5 EFSA OpenFoodTox (complementario)
- Dataset descargable + paquete R; aporta *reference points* y valores de referencia toxicológica (menos granular para irritación dérmica puntual).

---

## 3. Endpoint propuesto para `app.py`

```
GET /api/data?cas={CAS}&endpoint={skin_irritation|eye_irritation|...}&lang=es
```

**Cadena de resolución (con fallback en cascada):**

```
1. QSAR Toolbox WebAPI   (si TOOLBOX_URL disponible)  → dato experimental + referencia
2. CompTox Hazard API     (si BACKEND tiene CCTE_API_KEY) → skin-eye irritation + source
3. PubChem GHS            (siempre, sin key)            → categoría GHS + fuente
```

**Forma de respuesta (normalizada):**

```json
{
  "query": { "cas": "71751-41-2", "name": "abamectina", "endpoint": "skin_irritation" },
  "records": [
    {
      "value": "No irritante / Not irritating",
      "ghs": "No clasificado para irritación cutánea",
      "study": "OECD TG 404 (rabbit)",
      "source_db": "QSAR Toolbox — Skin irritation/corrosion ECHA",
      "reference": "…",
      "url": "…",
      "reliability": "Klimisch 1/2 (si disponible)"
    }
  ],
  "summary_cited": "Texto generado por Gemini citando ÚNICAMENTE las 'source_db'/'reference' anteriores",
  "disclaimer": "Dato de referencia; verificar vigencia y aplicabilidad regulatoria."
}
```

**Reglas de la capa Gemini:**
- Recibe SOLO el array `records`.
- Prohibido añadir valores o referencias no presentes en `records`.
- Si `records` está vacío → decir explícitamente "sin datos en las fuentes conectadas", no rellenar.

---

## 4. Ejemplo aplicado — irritación dérmica de ABAMECTINA

**Identidad:** CAS **71751-41-2** (abamectina / avermectina B1)

| Paso | Llamada | Resultado esperado |
|---|---|---|
| 1. Resolver | `Toolbox /substances/search?q=71751-41-2` | ID de sustancia en el Toolbox |
| 2. Datos | `Toolbox /category/datamatrix` (endpoint *Skin irritation/corrosion*) | Registro(s) experimental(es) **+ referencia** |
| 3. Fallback A | CompTox `/chemical/search/equal/71751-41-2` → DTXSID → Hazard skin-eye | Registro ToxValDB + source |
| 4. Fallback B | PubChem `name/abamectin/cids` → PUG-View GHS | Categoría GHS + fuente |
| 5. Formateo | Gemini sobre `records` | Resumen en español **citando** cada fuente |

> Cada valor devuelto arrastra su **procedencia** (DB + estudio/TG + URL). Esa es la cita — el LLM no la genera.

---

## 5. Cambios de configuración necesarios (cuando se implemente)

Añadir a `.env` / `.env.example`:

```
CCTE_API_KEY=          # opcional; habilita el fallback CompTox (EPA)
```

Sin claves nuevas: funciona con Toolbox (si está) + PubChem. Con `CCTE_API_KEY`: se activa el fallback ToxValDB.

---

## 6. Limitaciones honestas

- **No hay** un único conector NL→dato-citado listo para usar; se ensambla de 2–3 APIs.
- **Cobertura variable por molécula y endpoint**: irritación dérmica está mejor cubierta en Toolbox/ToxValDB/GHS que, por ejemplo, en EFSA OpenFoodTox.
- **eChemPortal / JMPR / Codex / FAO Specs / PPDB**: sin API limpia → quedan como enlace de verificación o RAG sobre PDF (fase posterior).
- El dato recuperado es **de referencia**: no sustituye el estudio GLP propietario del expediente (ver `FUENTES_DOSSIERS_AGROQUIMICOS.md`).

---

*Documento de diseño para el proyecto QSAR LLM (UranoIA). No implementado; sujeto a validación de endpoints del QSAR Toolbox v4.8 contra su Swagger local.*
