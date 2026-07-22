# Repositorios de Hugging Face útiles para Regulator.ia

**Modelos y datasets abiertos que complementan el stack QSAR + el lado documental regulatorio.**

Proyecto: QSAR LLM / Regulator.ia — UranoIA · Última actualización: 2026-07-19

> ⚠️ **Nota de encuadre regulatorio (léela primero):** casi todos estos modelos fueron entrenados para *drug discovery* / biomedicina, **no** para agroquímicos específicamente. Son útiles como **cribado (screening), priorización y apoyo a RAG**, pero **no** sustituyen las evaluaciones de referencia (JMPR/EFSA/EPA) ni los estudios GLP. Para uso regulatorio hay que **validar/fine-tunear con datos agroquímicos** y documentar la incertidumbre (dominio de aplicabilidad, guías OCDE). Ver `FUENTES_DOSSIERS_AGROQUIMICOS.md`.
>
> **Hallazgo (búsqueda en vivo en el HF Hub, 2026-07):** **no existe un modelo ni dataset específico de agroquímicos/pesticidas** con adopción relevante en el Hub. Las búsquedas por "pesticide/agrochemical/ecotoxicity" no devuelven repos consolidados. Esto confirma que la estrategia correcta es **usar los modelos cheminformáticos generales de abajo + fine-tuning con tus propios datos regulatorios**, no buscar un modelo "llave en mano" para el sector.

---

## 1. Predicción molecular / QSAR (SMILES → propiedad / toxicidad)
Complementan y permiten **contrastar** las predicciones del QSAR Toolbox.

| Repo | Qué es | Uso en Regulator.ia |
|---|---|---|
| `seyonec/ChemBERTa-zinc-base-v1` | Transformer tipo RoBERTa sobre SMILES (ZINC/PubChem) | Base para fine-tuning de tox/propiedades; embeddings de moléculas |
| `DeepChem/ChemBERTa-77M-MTR` | ChemBERTa 77M multi-task **regression** | Predicción de propiedades continuas (solubilidad, logP…) |
| `DeepChem/ChemBERTa-77M-MLM` | ChemBERTa 77M *masked LM* | Backbone para clasificación tox (Tox21, ClinTox) |
| `ibm-research/MoLFormer-XL-both-10pct` | Modelo fundacional molecular de IBM (SMILES), 46.8M params, Apache-2.0 | Embeddings potentes / read-across por similitud latente |

- ChemBERTa (7.1M descargas): https://huggingface.co/seyonec/ChemBERTa-zinc-base-v1
- ChemBERTa-77M-MTR (5.0M descargas): https://huggingface.co/DeepChem/ChemBERTa-77M-MTR
- MoLFormer-XL (8.6M descargas, **namespace `ibm-research`**): https://huggingface.co/ibm-research/MoLFormer-XL-both-10pct
- Ecosistema DeepChem (tutoriales Tox21/transfer learning): https://deepchem.io/

> **Idea de uso:** un endpoint tipo "segunda opinión" que corre ChemBERTa/MolFormer sobre el SMILES y **compara** con el Toolbox; si divergen, se marca para revisión humana.

---

## 2. Datasets toxicológicos de referencia (benchmark / fine-tuning)

| Repo | Contenido | Uso |
|---|---|---|
| `scikit-fingerprints/MoleculeNet_Tox21` | Tox21: 12 ensayos in vitro (NR + estrés) | Entrenar/validar clasificadores de toxicidad |
| `katielink/moleculenet-benchmark` | Suite MoleculeNet (ClinTox, SIDER, BBBP, BACE, ESOL…) | Benchmark estandarizado de endpoints ADMET/tox |
| Therapeutics Data Commons (TDC) | 66+ datasets ADMET/tox (Skin Reaction, hERG, DILI, Ames…) | Fuente amplia para endpoints regulatorios; vía librería `PyTDC` |

- Tox21 en HF: https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_Tox21
- MoleculeNet benchmark: https://huggingface.co/datasets/katielink/moleculenet-benchmark
- TDC (ADMET/tox): https://tdcommons.ai/

> **Relevante para tu caso:** TDC incluye endpoints muy cercanos a lo regulatorio (Ames mutagenicity, Skin Reaction, hERG, DILI). Buen punto de partida para modelos propios que citen su dataset de origen.

---

## 3. RAG multilingüe sobre dossiers regulatorios (español)
Para el buscador citado (`CONECTOR_DATOS_CITADOS.md`) y para consultar PDFs de JMPR/EFSA/EPA/SAG en español.

| Repo | Función | Por qué |
|---|---|---|
| `BAAI/bge-m3` | **Embeddings** multilingües (100+ idiomas, 8192 tokens, denso+léxico+ColBERT) | SOTA multilingüe; ideal para docs regulatorios ES/EN/PT largos |
| `BAAI/bge-reranker-v2-m3` | **Reranker** cross-encoder multilingüe | Filtra el top-k del retriever → mucha más precisión de cita |
| `intfloat/multilingual-e5-large` | Embeddings multilingües (alternativa) | Segunda opción robusta si bge-m3 no encaja |
| `NeuML/pubmedbert-base-embeddings` | Embeddings biomédicos (EN) | Para corpus toxicológico en inglés (JMPR/EFSA) |

- bge-m3: https://huggingface.co/BAAI/bge-m3
- bge-reranker-v2-m3: https://huggingface.co/BAAI/bge-reranker-v2-m3
- Para NER/clasificación en **español** biomédico también existen los modelos `PlanTL-GOB-ES/*` (RoBERTa biomédico-clínico español) — *verificar ID vigente en el Hub*.

> **Arquitectura sugerida:** `bge-m3` (retriever) + `bge-reranker-v2-m3` (reranker) sobre un índice de los PDFs oficiales → pasa los pasajes recuperados a Gemini para respuesta **citada**. Encaja directo con el principio de RAG-con-procedencia ya documentado.

---

## 4. Extracción de información de PDFs regulatorios (parsing + NER químico)
Para ingerir monografías/RAR/RED (PDF) y extraer entidades químicas y valores.

| Repo | Función | Uso |
|---|---|---|
| `pruas/BENT-PubMedBERT-NER-Chemical` | NER de entidades **químicas** | Detectar nombres/CAS de sustancias en el texto del dossier |
| `facebook/nougat-base` | OCR de documentos científicos (PDF→markdown, fórmulas/tablas) | Convertir PDFs escaneados de JMPR/EFSA a texto estructurado — ⚠️ **licencia CC-BY-NC-4.0 (no comercial)** |
| `ds4sd/docling-models` (IBM Docling) | Parsing de layout/tablas de PDF (licencia permisiva) | Extraer tablas de LMR/endpoints — **preferible a Nougat para uso comercial** |

- Chemical NER: https://huggingface.co/pruas/BENT-PubMedBERT-NER-Chemical
- Nougat (OCR científico): https://huggingface.co/facebook/nougat-base
- Docling: https://github.com/DS4SD/docling

> **Pipeline documental:** PDF → (Nougat/Docling) texto+tablas → (BENT-NER) entidades químicas → índice para RAG (§3). Así conviertes los dossiers públicos en un corpus consultable y citable.

---

## 5. Cómo encajan en el stack actual

```
Regulator.ia
├── Predicción       → QSAR Toolbox WebAPI  +  ChemBERTa/MolFormer (2ª opinión)   [§1]
├── Datos/benchmark  → CompTox/PubChem       +  Tox21/MoleculeNet/TDC (validación) [§2]
├── RAG citado       → bge-m3 + bge-reranker-v2-m3 sobre dossiers oficiales        [§3]
└── Ingesta docs     → Nougat/Docling + BENT-NER-Chemical (PDF → corpus)           [§4]
```

Prioridad práctica sugerida:
1. **§3 (RAG multilingüe)** — mayor impacto inmediato para "buscar y citar" en tus dossiers.
2. **§4 (ingesta PDF)** — habilita el corpus para el RAG.
3. **§1 (2ª opinión QSAR)** — refuerza la confianza vs. Toolbox.
4. **§2 (datasets)** — solo si vas a entrenar/validar modelos propios.

---

## 6. Limitaciones y buenas prácticas

- **Sesgo de dominio:** modelos entrenados en fármacos; validar en agroquímicos antes de cualquier uso decisorio.
- **Licencias:** revisar la licencia de cada repo (MoLFormer, datasets) antes de uso comercial/consultoría.
- **Trazabilidad:** en RAG, la cita debe apuntar al **PDF oficial** (JMPR/EFSA/EPA/SAG), no al modelo. El modelo solo recupera/formatea.
- **No sustituyen GLP ni evaluaciones de referencia.** Son cribado y apoyo, bajo el disclaimer regulatorio del proyecto.

---

*Documento de referencia para el proyecto QSAR LLM / Regulator.ia (UranoIA). IDs de repos verificados en el Hugging Face Hub a la fecha; confirmar vigencia antes de integrar.*
