from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory
from botbuilder.dialogs import ComponentDialog
from models.evento import Evento
from storage.database import guardar_evento

REPORTE_DIALOG = "ReporteDialog"
WATERFALL_DIALOG = "WaterfallDialog"
TEXT_PROMPT = "TextPrompt"
CHOICE_PROMPT = "ChoicePrompt"


class ReporteDialog(ComponentDialog):
    def __init__(self):
        super().__init__(REPORTE_DIALOG)
        self.add_dialog(TextPrompt(TEXT_PROMPT))
        self.add_dialog(ChoicePrompt(CHOICE_PROMPT))
        self.add_dialog(
            WaterfallDialog(WATERFALL_DIALOG, [
                self.paso_fecha,
                self.paso_hora,
                self.paso_tipo_red,
                self.paso_site,
                self.paso_categoria,
                self.paso_titulo,
                self.paso_determinante,
                self.paso_descripcion,
                self.paso_planes_accion,
                self.paso_personal_enterado,
                self.paso_importe,
                self.paso_confirmar,
            ])
        )
        self.initial_dialog_id = WATERFALL_DIALOG

    async def paso_fecha(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"] = Evento()
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("📅 ¿Cuál es la **Fecha del Evento**? (DD/MM/YYYY)")
        ))

    async def paso_hora(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].fecha_evento = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("🕐 ¿A qué **Hora** ocurrió el evento? (HH:MM)")
        ))

    async def paso_tipo_red(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].hora_evento = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("🔗 ¿Cuál es el **Tipo de RED**?\n(Ej: Perecederos, Seco, General)")
        ))

    async def paso_site(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].tipo_red = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("📍 ¿Cuál es el **Site**? (Ej: SMO, GDL, MTY)")
        ))

    async def paso_categoria(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].site = step.result
        return await step.prompt(CHOICE_PROMPT, PromptOptions(
            prompt=MessageFactory.text("⚠️ ¿Cuál es la **Categoría** del evento?"),
            choices=[Choice("Alto"), Choice("Medio"), Choice("Bajo")]
        ))

    async def paso_titulo(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].categoria = step.result.value
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("📌 ¿Cuál es el **Título del Evento**?")
        ))

    async def paso_determinante(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].titulo_evento = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text(
                "🏪 ¿Aplica **Determinante y Tienda**?\n"
                "*(Solo para Visita a Tienda — escribe los datos o escribe **no** si no aplica)*"
            )
        ))

    async def paso_descripcion(self, step: WaterfallStepContext) -> DialogTurnResult:
        respuesta = step.result.strip().lower()
        step.values["evento"].determinante_tienda = None if respuesta == "no" else step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("📝 Escribe la **Descripción del Evento** con todos los detalles:")
        ))

    async def paso_planes_accion(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].descripcion_evento = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("✅ ¿Cuáles son los **Planes de Acción o Seguimiento**?")
        ))

    async def paso_personal_enterado(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].planes_accion = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text(
                "👥 ¿Quién fue el **Personal Enterado**?\n"
                "*(Separa con comas si son varios — Ej: CAE, Gerencia operativa, Gerencia PA)*"
            )
        ))

    async def paso_importe(self, step: WaterfallStepContext) -> DialogTurnResult:
        step.values["evento"].personal_enterado = step.result
        return await step.prompt(TEXT_PROMPT, PromptOptions(
            prompt=MessageFactory.text("💰 ¿Cuál es el **Importe**? (escribe 0 si no hay costo)")
        ))

    async def paso_confirmar(self, step: WaterfallStepContext) -> DialogTurnResult:
        evento: Evento = step.values["evento"]
        evento.importe = step.result

        evento_id = guardar_evento(evento)

        resumen = evento.resumen()
        await step.context.send_activity(
            MessageFactory.text(f"✅ **Evento registrado correctamente** (ID: {evento_id})\n\n{resumen}")
        )
        return await step.end_dialog()
