import re

FIELDS_CONFIG = [
    {"label": "Fecha del Evento",                "key": "fecha_evento",        "required": True},
    {"label": "Hora del Evento",                 "key": "hora_evento",         "required": True},
    {"label": "Tipo de RED",                     "key": "tipo_red",            "required": True},
    {"label": "Site",                            "key": "site",                "required": True},
    {"label": "Categoría",                       "key": "categoria",           "required": True},
    {"label": "Título del Evento",               "key": "titulo_evento",       "required": True},
    {"label": "Determinante y Tienda",           "key": "determinante_tienda", "required": False},
    {"label": "Descripción del Evento",          "key": "descripcion_evento",  "required": True},
    {"label": "Planes de Acción o seguimiento",  "key": "planes_accion",       "required": True},
    {"label": "Personal Enterado",               "key": "personal_enterado",   "required": True},
    {"label": "Importe",                         "key": "importe",             "required": True},
]

_SOLO_APLICA_RE = re.compile(r"\(Solo aplica para Visita a Tienda\)", re.IGNORECASE)


def parse_event_message(text: str) -> dict:
    labels = [f["label"] for f in FIELDS_CONFIG]
    result = {}

    for i, cfg in enumerate(FIELDS_CONFIG):
        label = cfg["label"]
        next_label = labels[i + 1] if i + 1 < len(labels) else None

        if next_label:
            pattern = rf"{re.escape(label)}:\s*(.*?)(?=\n{re.escape(next_label)}:|\Z)"
        else:
            pattern = rf"{re.escape(label)}:\s*(.*?)(?:\Z)"

        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            value = _SOLO_APLICA_RE.sub("", match.group(1)).strip()
            result[cfg["key"]] = value or None
        else:
            result[cfg["key"]] = None

    return result


def validate_event(event_data: dict) -> list[str]:
    missing = []
    for cfg in FIELDS_CONFIG:
        if cfg["required"] and not event_data.get(cfg["key"]):
            missing.append(cfg["label"])
    return missing


def is_event_message(text: str) -> bool:
    trigger_fields = ["Fecha del Evento", "Tipo de RED", "Descripción del Evento"]
    return sum(1 for f in trigger_fields if f in text) >= 2
