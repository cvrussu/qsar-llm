"""
QSAR LLM Backend — UranoIA
API Flask que conecta el frontend con el OECD QSAR Toolbox y Claude AI
Autor: UranoIA / Claudio Valdés Russu
Versión: 1.0.0-beta
"""

import os
import json
import re
import logging
import requests
from datetime import datetime
from functools import wraps
from typing import Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("QSAR-LLM")

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, origins=["*"])  # Adjust for production

# QSAR Toolbox REST API base URL (local installation)
TOOLBOX_URL = os.environ.get("TOOLBOX_URL", "http://localhost:3000")

# Anthropic API key
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ──────────────────────────────────────────────
# AUTH MIDDLEWARE (disabled for beta)
# ──────────────────────────────────────────────
def require_key(f):
    """Auth desactivada en beta — acceso abierto."""
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated

# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ──────────────────────────────────────────────
# STATUS ENDPOINT
# ──────────────────────────────────────────────
@app.route("/api/status")
def status():
    """Check connectivity with QSAR Toolbox and report version."""
    toolbox_ok = False
    toolbox_version = "4.8"

    try:
        r = requests.get(f"{TOOLBOX_URL}/api/v1/version", timeout=4)
        if r.ok:
            toolbox_ok = True
            data = r.json()
            toolbox_version = data.get("version", "4.8")
    except Exception:
        pass

    return jsonify({
        "status": "online",
        "version": toolbox_version,
        "toolbox_connected": toolbox_ok,
        "anthropic_configured": bool(ANTHROPIC_KEY),
        "timestamp": datetime.utcnow().isoformat(),
    })

# ──────────────────────────────────────────────
# QSAR TOOLBOX HELPERS
# ──────────────────────────────────────────────

def toolbox_get(endpoint: str, params: dict = None) -> Optional[dict]:
    """Generic GET request to QSAR Toolbox REST API."""
    try:
        url = f"{TOOLBOX_URL}/api/v1/{endpoint}"
        r = requests.get(url, params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"Toolbox GET {endpoint} failed: {e}")
        return None


def toolbox_post(endpoint: str, payload: dict) -> Optional[dict]:
    """Generic POST request to QSAR Toolbox REST API."""
    try:
        url = f"{TOOLBOX_URL}/api/v1/{endpoint}"
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"Toolbox POST {endpoint} failed: {e}")
        return None


def resolve_cas_from_name(name: str) -> Optional[str]:
    """Attempt to resolve a chemical name to CAS using PubChem."""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(name)}/property/IUPACName,MolecularFormula,MolecularWeight,XLogP/JSON"
        r = requests.get(url, timeout=10)
        if r.ok:
            props = r.json()["PropertyTable"]["Properties"][0]
            return props
    except Exception:
        pass
    return None


def get_pubchem_data(cas_or_name: str) -> Optional[dict]:
    """Fetch basic compound data from PubChem as fallback."""
    try:
        # Try by CAS first
        if re.match(r'\d{2,7}-\d{2}-\d', cas_or_name):
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas_or_name}/property/IUPACName,MolecularFormula,MolecularWeight,XLogP,IsomericSMILES/JSON"
        else:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(cas_or_name)}/property/IUPACName,MolecularFormula,MolecularWeight,XLogP,IsomericSMILES/JSON"

        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            props = data["PropertyTable"]["Properties"][0]
            return {
                "cid": props.get("CID"),
                "formula": props.get("MolecularFormula"),
                "mw": f"{props.get('MolecularWeight', 'N/D')} g/mol",
                "logKow": str(props.get("XLogP", "N/D")),
                "smiles": props.get("IsomericSMILES"),
                "iupac": props.get("IUPACName"),
            }
    except Exception as e:
        log.warning(f"PubChem lookup failed: {e}")
    return None


def run_toolbox_analysis(query: str, options: dict) -> dict:
    """
    Orchestrate QSAR Toolbox analysis:
    1. Resolve molecule identity
    2. Run profiling modules
    3. Build category and data matrix
    4. Return structured results
    """
    # Extract CAS or molecule name
    cas_match = re.search(r'\b(\d{2,7}-\d{2}-\d)\b', query)
    cas = cas_match.group(1) if cas_match else None

    results = {
        "query": query,
        "cas": cas,
        "toolbox_data": None,
        "pubchem_data": None,
        "profiling": None,
        "category": None,
        "endpoints": [],
    }

    # Step 1: Molecule identification via QSAR Toolbox
    if cas:
        tb_mol = toolbox_get("substances/search", {"cas": cas})
        if tb_mol:
            results["toolbox_data"] = tb_mol

    # Step 2: PubChem enrichment (fallback or complement)
    identifier = cas or query
    pc_data = get_pubchem_data(identifier)
    if pc_data:
        results["pubchem_data"] = pc_data

    # Step 3: Profiling (if enabled)
    if options.get("profiling") and cas:
        profiling = toolbox_post("profiling/run", {
            "cas": cas,
            "profilers": ["mutagenicity", "aquatic_toxicity", "skin_sensitization"]
        })
        results["profiling"] = profiling

    # Step 4: Category and read-across (if enabled)
    if options.get("readAcross") and cas:
        category = toolbox_post("category/build", {"cas": cas})
        results["category"] = category

    return results


# ──────────────────────────────────────────────
# SYSTEM PROMPT FOR CLAUDE
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """Eres QSAR LLM, un agente especializado en evaluación regulatoria de agroquímicos mediante el OECD QSAR Toolbox v4.8.

## Tu rol
Asistes a consultores y expertos regulatorios en:
- Análisis toxicológico in silico de principios activos y metabolitos de agroquímicos
- Interpretación de resultados del QSAR Toolbox (perfilado, read-across, categorías)
- Evaluación de endpoints: mutagenicidad (Ames), toxicidad acuática (EC50, LC50, NOEC), sensibilización cutánea (DASSAW), biodegradabilidad
- Cumplimiento regulatorio: REACH (UE), Reglamento 1107/2009 (plaguicidas UE), ANVISA (Brasil), EPA (EEUU), marcos OCDE

## Marco regulatorio de referencia
- OECD TG 497: Defined Approaches para sensibilización cutánea
- Guía OCDE 114: Validación de métodos QSAR
- REACH Anexo XI: Criterios para datos in silico
- Reglamento 1107/2009/CE: Registro de productos fitosanitarios UE
- FAO/OMS: Codex Alimentarius y BPAs

## Formato de respuesta
- Usa markdown con encabezados, listas y énfasis
- Sé técnico pero accesible para profesionales regulatorios
- Incluye siempre: identidad molecular, análisis de riesgo y contexto regulatorio
- Cuando hay datos del Toolbox, interprételos con criterio científico
- Indica incertidumbre y limitaciones de las predicciones in silico
- Responde en el idioma indicado (por defecto español)
- Para preguntas no relacionadas con química/regulatorio, redirige amablemente

## Importante
Las predicciones in silico son herramientas de apoyo, no reemplazan ensayos experimentales certificados GLP.
"""


def build_llm_prompt(query: str, toolbox_results: dict, language: str) -> str:
    """Construct the full prompt for Claude with context."""
    lang_instruction = {
        "es": "Responde en español.",
        "en": "Respond in English.",
        "pt": "Responda em português.",
    }.get(language, "Responde en español.")

    context_parts = [f"**Consulta del usuario:** {query}\n"]

    if toolbox_results.get("cas"):
        context_parts.append(f"**Número CAS identificado:** {toolbox_results['cas']}")

    if toolbox_results.get("pubchem_data"):
        pc = toolbox_results["pubchem_data"]
        context_parts.append(
            f"**Datos PubChem:**\n"
            f"- Fórmula: {pc.get('formula', 'N/D')}\n"
            f"- Peso molecular: {pc.get('mw', 'N/D')}\n"
            f"- log Kow (XLogP): {pc.get('logKow', 'N/D')}\n"
            f"- IUPAC: {pc.get('iupac', 'N/D')}\n"
            f"- SMILES: {pc.get('smiles', 'N/D')}"
        )

    if toolbox_results.get("toolbox_data"):
        context_parts.append(
            f"**Datos QSAR Toolbox:** {json.dumps(toolbox_results['toolbox_data'], ensure_ascii=False, indent=2)}"
        )

    if toolbox_results.get("profiling"):
        context_parts.append(
            f"**Resultados de perfilado:** {json.dumps(toolbox_results['profiling'], ensure_ascii=False, indent=2)}"
        )

    context_parts.append(f"\n{lang_instruction}")
    context_parts.append(
        "Proporciona un análisis regulatorio completo, técnico y bien estructurado."
    )

    return "\n\n".join(context_parts)


# ──────────────────────────────────────────────
# MAIN CHAT ENDPOINT
# ──────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@require_key
def chat():
    """Main chat endpoint: orchestrates Toolbox + Claude."""
    try:
        body = request.get_json(force=True)
        query = body.get("query", "").strip()
        options = body.get("options", {})
        model = body.get("model", "claude-3-5-sonnet-20241022")
        language = body.get("language", "es")

        if not query:
            return jsonify({"error": "Query vacío"}), 400

        log.info(f"Chat query: {query[:80]}…")

        # Step 1: Run QSAR Toolbox analysis
        toolbox_results = run_toolbox_analysis(query, options)

        # Step 2: Build prompt
        user_prompt = build_llm_prompt(query, toolbox_results, language)

        # Step 3: Call Claude
        if not ANTHROPIC_KEY:
            return jsonify({"error": "ANTHROPIC_API_KEY no configurado"}), 503

        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        response_text = message.content[0].text

        # Step 4: Build structured card data (if molecule found)
        card_data = None
        if toolbox_results.get("cas") and toolbox_results.get("pubchem_data"):
            pc = toolbox_results["pubchem_data"]
            cas = toolbox_results["cas"]

            card_data = {
                "molecule": {
                    "cas": cas,
                    "name": body.get("moleculeName", cas),
                    "formula": pc.get("formula"),
                    "mw": pc.get("mw"),
                    "logKow": pc.get("logKow"),
                    "smiles": pc.get("smiles"),
                },
                "endpoints": [],
                "alerts": [],
            }

            # Parse profiling alerts if available
            if toolbox_results.get("profiling"):
                prof = toolbox_results["profiling"]
                if isinstance(prof, dict):
                    alerts = prof.get("alerts", [])
                    for alert in alerts[:6]:
                        card_data["alerts"].append({
                            "text": alert.get("name", "Alerta"),
                            "level": "amber" if alert.get("risk") == "low" else "red"
                        })

        return jsonify({
            "message": response_text,
            "data": card_data,
            "toolbox_connected": toolbox_results.get("toolbox_data") is not None,
            "pubchem_enriched": toolbox_results.get("pubchem_data") is not None,
            "cas": toolbox_results.get("cas"),
            "timestamp": datetime.utcnow().isoformat(),
        })

    except anthropic.APIError as e:
        log.error(f"Anthropic API error: {e}")
        return jsonify({"error": f"Error de API: {str(e)}"}), 502
    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


# ──────────────────────────────────────────────
# DIRECT TOOLBOX ENDPOINTS (proxy)
# ──────────────────────────────────────────────
@app.route("/api/toolbox/search")
@require_key
def toolbox_search():
    """Search substance in QSAR Toolbox by CAS or name."""
    identifier = request.args.get("q", "")
    if not identifier:
        return jsonify({"error": "Parámetro 'q' requerido"}), 400

    data = toolbox_get("substances/search", {"query": identifier})
    if data is None:
        return jsonify({"error": "Toolbox no disponible", "fallback": True}), 503

    return jsonify(data)


@app.route("/api/toolbox/profile", methods=["POST"])
@require_key
def toolbox_profile():
    """Run profiling for a CAS number."""
    body = request.get_json(force=True)
    cas = body.get("cas")
    if not cas:
        return jsonify({"error": "CAS requerido"}), 400

    data = toolbox_post("profiling/run", {
        "cas": cas,
        "profilers": body.get("profilers", ["all"])
    })

    if data is None:
        return jsonify({"error": "Toolbox no disponible"}), 503

    return jsonify(data)


@app.route("/api/toolbox/category", methods=["POST"])
@require_key
def toolbox_category():
    """Build chemical category for a CAS number."""
    body = request.get_json(force=True)
    cas = body.get("cas")
    if not cas:
        return jsonify({"error": "CAS requerido"}), 400

    data = toolbox_post("category/build", {"cas": cas})
    if data is None:
        return jsonify({"error": "Toolbox no disponible"}), 503

    return jsonify(data)


@app.route("/api/pubchem")
def pubchem_lookup():
    """PubChem lookup proxy — no auth required."""
    identifier = request.args.get("q", "")
    if not identifier:
        return jsonify({"error": "Parámetro 'q' requerido"}), 400

    data = get_pubchem_data(identifier)
    if data:
        return jsonify(data)
    return jsonify({"error": "No encontrado en PubChem"}), 404


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    log.info("=" * 60)
    log.info("  QSAR LLM — UranoIA Backend")
    log.info(f"  Puerto: {port}")
    log.info(f"  QSAR Toolbox URL: {TOOLBOX_URL}")
    log.info(f"  Anthropic API: {'✓ Configurado' if ANTHROPIC_KEY else '✗ Falta ANTHROPIC_API_KEY'}")
    log.info("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=debug)
