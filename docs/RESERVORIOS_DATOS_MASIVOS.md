# Reservorios de datos regulatorios (bulk / masivos)

**Bases de datos estructuradas y descargables en bloque** — a diferencia de las fuentes por-molécula de `FUENTES_DOSSIERS_AGROQUIMICOS.md` (un PDF por sustancia), estos reservorios permiten poblar un corpus/base local de una sola vez, con miles de sustancias y registros ya estructurados y citables.

Proyecto: QSAR LLM / Regulator.ia — UranoIA · Última actualización: 2026-07-22

> **Por qué importa la distinción:** un PDF de JMPR o un RAR de EFSA es la evaluación de *una* sustancia. Un reservorio bulk es una base de datos completa (miles de sustancias) que se descarga o consulta por lotes — es la materia prima para: (a) el RAG/conector citado (`CONECTOR_DATOS_CITADOS.md`), (b) entrenar/validar modelos QSAR propios (`HUGGINGFACE_REPOS_REGULATORIA.md`), (c) construir una base local de referencia para Regulator.ia.

---

## 1. EFSA OpenFoodTox ⭐ (el más valioso para citación)

Base de datos toxicológica estructurada de la EFSA — resume evaluaciones de +5.700 sustancias únicas en +2.400 dictámenes/conclusiones científicas, incluyendo **plaguicidas, aditivos, contaminantes y sustancias de pienso**.

**Seis planillas descargables:**
1. Caracterización de sustancia (identidad, CAS, sinónimos)
2. Outputs de EFSA (referencia al dictamen/opinión de origen)
3. **Reference points** (NOAEL, LOAEL, BMDL, LD50, NOEC ecotoxicológico) — el dato "citable" por excelencia
4. **Reference values** (ADI, ARfD, AOEL)
5. Genotoxicidad
6. Fisicoquímica y toxicocinética

- Descarga/infografía oficial: https://www.efsa.europa.eu/en/discover/infographics/openfoodtox-chemical-hazards-database
- Archivo permanente con DOI (Zenodo): https://zenodo.org/records/8120114
- Editorial descriptivo (EFSA Journal): https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2017.e15011

> **Uso ideal:** cada fila ya trae `sustancia + reference point + valor + dictamen de origen` — es prácticamente el formato de "registro citable" que necesita el conector (`records[]` en `CONECTOR_DATOS_CITADOS.md`). Prioridad **alta** para integrar primero.

---

## 2. US EPA ECOTOX Knowledgebase

La mayor base de ecotoxicidad pública: +1.000.000 registros de ensayo, +12.000 químicos, +13.000 especies acuáticas/terrestres, compilados de +53.000 referencias revisadas por pares.

- Portal: https://www.epa.gov/comptox-tools/ecotoxicology-ecotox-knowledgebase-resource-hub
- **Descarga bulk programática:** paquete R `ECOTOXr` — descarga las tablas crudas y arma una base SQLite local: https://cran.r-project.org/package=ECOTOXr
- Contacto soporte: ecotox.support@epa.gov

### 2.1 OPP Pesticide Ecotoxicity Database (subconjunto específico de plaguicidas)
Resumen actualizado de **todos los datos ecotoxicológicos revisados por EPA de ingredientes activos de plaguicidas** (registrados o históricos en EE.UU.) — el subconjunto más directamente relevante para Regulator.ia.

- Portal: https://ecotox.ipmcenters.org/index.cfm?menuid=2
- Indexado también en PubChem como fuente: https://pubchem.ncbi.nlm.nih.gov/source/15219

---

## 3. ECHA — REACH Study Results (bulk IUCLID)

Descarga masiva de **dossiers de registro REACH no confidenciales**, en formato IUCLID, para ~23.000 sustancias.

- Portal IUCLID: https://iuclid6.echa.europa.eu/
- Manual de difusión/confidencialidad REACH: https://echa.europa.eu/documents/10162/22308542/manual_dissemination_en.pdf
- **Herramientas de análisis:** IUCLID 6 API, IUCLID Data Extractor, o búsqueda avanzada IUCLID

> Nota: cubre sustancias químicas industriales bajo REACH; los ingredientes activos de plaguicidas están regulados aparte (Reg. 1107/2009) pero muchos aparecen también en REACH por otros usos — verificar caso a caso.

---

## 4. EPA CompTox Chemicals Dashboard / DSSTox

Base de identidad + propiedades + toxicidad + bioensayos para **~760.000 sustancias**, con +300 listas curadas (structure- or category-based).

- Dashboard: https://comptox.epa.gov/dashboard/
- Descargas: https://comptox.epa.gov/dashboard/downloads
- **Batch search:** mapeo de cientos/miles de identificadores químicos de una vez, con descarga de múltiples streams de datos
- Ya conectable vía API (ver `CONECTOR_DATOS_CITADOS.md` §2.2 — CCTE Hazard API)

> Revisar si existe una de las +300 listas curadas específica de **plaguicidas registrados** (ej. listas EPA OPP) para acotar el universo de sustancias relevante.

---

## 5. Otros reservorios ya documentados (referencia cruzada)

| Reservorio | Cobertura | Documentado en |
|---|---|---|
| JMPR (FAO/WHO) | Toxicología/residuos por sustancia | `FUENTES_DOSSIERS_AGROQUIMICOS.md` §1.1 |
| FAO/WHO Specifications | Identidad/pureza/equivalencia | `FUENTES_DOSSIERS_AGROQUIMICOS.md` §1.2 |
| Codex Alimentarius (LMR) | LMR internacionales, base consultable | `FUENTES_DOSSIERS_AGROQUIMICOS.md` §1.6 |
| PPDB (Univ. Hertfordshire) | Propiedades consolidadas por sustancia | `FUENTES_DOSSIERS_AGROQUIMICOS.md` §2.1 |
| Open EFSA (estudios crudos) | Dossier completo de renovación (caso glifosato) | `FUENTES_DOSSIERS_AGROQUIMICOS.md` §6b |
| Datasets HF (Tox21, MoleculeNet, TDC) | Benchmarks de ML, no regulatorios pero útiles para validar modelos | `HUGGINGFACE_REPOS_REGULATORIA.md` §2 |

---

## 6. Matriz de prioridad de integración

| Reservorio | Relevancia agroquímicos | Facilidad de acceso | Prioridad |
|---|---|---|---|
| **EFSA OpenFoodTox** | Alta (incluye plaguicidas explícitamente) | Alta (Excel + Zenodo) | 🥇 1ª |
| **OPP Pesticide Ecotoxicity DB** | Máxima (100% plaguicidas) | Media (portal propio) | 🥈 2ª |
| **EPA ECOTOX Knowledgebase** | Media-alta (ecotox general, incluye plaguicidas) | Media (requiere `ECOTOXr` o descarga completa) | 🥉 3ª |
| **CompTox/DSSTox** | Media (universo amplio, no plaguicida-específico) | Alta (ya tienes la API vía CCTE) | 3ª (en paralelo, ya cableado) |
| **ECHA REACH bulk (IUCLID)** | Baja-media (no es el régimen de plaguicidas) | Baja (requiere IUCLID local) | 4ª / opcional |

---

## 7. Cómo se integra con lo ya diseñado

```
Regulator.ia
├── Dossiers por sustancia (PDF)     → FUENTES_DOSSIERS_AGROQUIMICOS.md   (JMPR, EFSA, EPA, SAG…)
├── Reservorios masivos (bulk)       → este documento                     (OpenFoodTox, ECOTOX, DSSTox…)
├── Conector citado (/api/data)      → CONECTOR_DATOS_CITADOS.md          (arquitectura RAG-con-procedencia)
└── Modelos/datasets ML              → HUGGINGFACE_REPOS_REGULATORIA.md   (ChemBERTa, MoLFormer, bge-m3…)
```

**Cambio propuesto al conector:** agregar **EFSA OpenFoodTox** como fuente adicional en la cadena de resolución de `CONECTOR_DATOS_CITADOS.md` §3, antes o junto a CompTox — ya que aporta `reference points` estructurados con cita directa al dictamen EFSA. Ver actualización en ese documento.

---

## 8. Limitaciones honestas

- Estos reservorios son bulk pero **no están unificados**: cada uno con su propio esquema, hay que normalizar antes de usarlos juntos.
- **ECHA REACH bulk** cubre química industrial, no el régimen específico de plaguicidas (Reg. 1107/2009) — su relevancia para Regulator.ia es secundaria.
- Ninguno reemplaza el estudio GLP propietario del expediente; siguen siendo **evaluaciones/datos de referencia** (ver disclaimer en `FUENTES_DOSSIERS_AGROQUIMICOS.md` §6).
- Descargas grandes (ECOTOX: +1M registros) requieren procesamiento/ETL antes de ser útiles — no es plug-and-play inmediato.

---

*Documento de referencia para el proyecto QSAR LLM / Regulator.ia (UranoIA). Verificar vigencia de enlaces y esquemas de descarga antes de integrar.*
