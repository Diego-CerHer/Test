from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Evento:
    fecha_evento: Optional[str] = None
    hora_evento: Optional[str] = None
    tipo_red: Optional[str] = None
    site: Optional[str] = None
    categoria: Optional[str] = None
    titulo_evento: Optional[str] = None
    determinante_tienda: Optional[str] = None
    descripcion_evento: Optional[str] = None
    planes_accion: Optional[str] = None
    personal_enterado: Optional[str] = None
    importe: Optional[str] = None
    creado_en: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def resumen(self) -> str:
        det = self.determinante_tienda if self.determinante_tienda else "N/A"
        return (
            f"📋 **REPORTE DE EVENTO**\n\n"
            f"📅 Fecha: {self.fecha_evento}\n"
            f"🕐 Hora: {self.hora_evento}\n"
            f"🔗 Tipo de RED: {self.tipo_red}\n"
            f"📍 Site: {self.site}\n"
            f"⚠️ Categoría: {self.categoria}\n"
            f"📌 Título: {self.titulo_evento}\n"
            f"🏪 Determinante y Tienda: {det}\n\n"
            f"📝 Descripción:\n{self.descripcion_evento}\n\n"
            f"✅ Planes de Acción:\n{self.planes_accion}\n\n"
            f"👥 Personal Enterado:\n{self.personal_enterado}\n\n"
            f"💰 Importe: ${self.importe}"
        )
