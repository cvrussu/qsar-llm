# Documentación de datos y modelos — Regulator.ia

Índice de los documentos de referencia sobre fuentes de datos regulatorios, modelos de IA/QSAR y arquitectura del conector citado, generados para el proyecto QSAR LLM / Regulator.ia (UranoIA).

Última actualización: 2026-07-22

---

## Mapa de documentos

| Documento | Responde a | Contenido |
|---|---|---|
| **[FUENTES_DOSSIERS_AGROQUIMICOS.md](./FUENTES_DOSSIERS_AGROQUIMICOS.md)** | "¿Qué fuentes confiables citar para un dossier de glifosato/clorpirifos/etc.?" | Fuentes internacionales (JMPR, EFSA, US EPA, Codex, ECHA), bases consolidadas (PPDB, PubChem), entes nacionales (SAG Chile, ANVISA/IBAMA/MAPA Brasil), ejemplos aplicados a glifosato y clorpirifos, y qué es público vs. protegido (GLP) |
| **[RESERVORIOS_DATOS_MASIVOS.md](./RESERVORIOS_DATOS_MASIVOS.md)** | "¿Hay bases de datos completas descargables en bloque, no solo un PDF por sustancia?" | EFSA OpenFoodTox, EPA ECOTOX/OPP Pesticide Ecotoxicity DB, ECHA REACH bulk (IUCLID), CompTox/DSSTox — con matriz de prioridad de integración |
| **[HUGGINGFACE_REPOS_REGULATORIA.md](./HUGGINGFACE_REPOS_REGULATORIA.md)** | "¿Qué modelos/datasets de Hugging Face sirven para Regulator.ia?" | Predicción molecular (ChemBERTa, MoLFormer), datasets tox (Tox21, MoleculeNet, TDC), RAG multilingüe (bge-m3, reranker), ingesta de PDF (Docling, NER químico) — con IDs verificados en vivo contra el Hub y notas de licencia |
| **[CONECTOR_DATOS_CITADOS.md](./CONECTOR_DATOS_CITADOS.md)** | "¿Cómo armo un buscador que responda 'dame X dato de Y molécula' citando la fuente?" | Diseño de arquitectura (RAG con procedencia), endpoint propuesto `/api/data`, cadena de fallback entre fuentes, ejemplo aplicado a irritación dérmica de abamectina |

---

## Cómo se relacionan

```
                    ┌─────────────────────────────────┐
                    │   CONECTOR_DATOS_CITADOS.md      │
                    │   (arquitectura: cómo se conecta  │
                    │    todo lo de abajo)              │
                    └────────────┬─────────────────────┘
                                 │ consume
        ┌────────────────────────┼────────────────────────┐
        │                        │                         │
┌───────▼────────┐    ┌──────────▼──────────┐    ┌─────────▼──────────┐
│ FUENTES_        │    │ RESERVORIOS_        │    │ HUGGINGFACE_        │
│ DOSSIERS_       │    │ DATOS_MASIVOS.md     │    │ REPOS_               │
│ AGROQUIMICOS.md │    │                      │    │ REGULATORIA.md       │
│                 │    │ Bases bulk           │    │                      │
│ Dossiers/PDF    │    │ descargables         │    │ Modelos ML/RAG       │
│ por sustancia   │    │ (miles de sustancias)│    │ (predicción, tox,    │
│ (JMPR/EFSA/EPA) │    │ (OpenFoodTox, ECOTOX)│    │  embeddings, NER)    │
└─────────────────┘    └──────────────────────┘    └──────────────────────┘
```

- **Fuentes por sustancia** (izquierda) → citar un dossier puntual en un expediente.
- **Reservorios masivos** (centro) → poblar una base local / corpus para consulta rápida y en bloque.
- **Modelos HF** (derecha) → predicción, RAG y extracción de información sobre lo anterior.
- **El conector** (arriba) → la pieza que los amarra en un solo endpoint `/api/data` con citación garantizada.

---

## Estado actual

Todo lo anterior es **documentación de diseño**; nada está implementado aún en `app.py`. Antes de codificar, define:

1. **Alcance del primer sprint** — ¿arrancamos con Toolbox + PubChem (sin claves nuevas) o incluimos CompTox/OpenFoodTox desde el día uno?
2. **Dónde vive el ETL de OpenFoodTox/ECOTOX** — estas son bulk, no REST en vivo; requieren una tabla local (SQLite/Postgres) con job de carga periódica.
3. **Validación de dominio** — los modelos HF (ChemBERTa, MoLFormer) están entrenados en fármacos; cualquier uso decisorio en agroquímicos necesita fine-tuning/validación propia antes de confiar en sus predicciones.

---

*Índice de documentación del proyecto QSAR LLM / Regulator.ia (UranoIA).*
