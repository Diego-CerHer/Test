from botbuilder.core import ActivityHandler, TurnContext, ConversationState, MessageFactory
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus
from botbuilder.core.integration import aiohttp_error_middleware


class BotIncidentes(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, dialog: Dialog):
        self.conversation_state = conversation_state
        self.dialog = dialog
        self.dialog_state = conversation_state.create_property("DialogState")

    async def on_message_activity(self, turn_context: TurnContext):
        dialog_set = DialogSet(self.dialog_state)
        dialog_set.add(self.dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        result = await dialog_context.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            texto = turn_context.activity.text.strip().lower() if turn_context.activity.text else ""

            if texto in ["hola", "nuevo", "reporte", "iniciar", "start", ""]:
                await dialog_context.begin_dialog(self.dialog.id)
            else:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "👋 Hola! Escribe **nuevo** o **reporte** para registrar un evento de incidencia."
                    )
                )

        await self.conversation_state.save_changes(turn_context)

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "👋 Bienvenido al **Bot de Incidencias**.\n\n"
                        "Escribe **nuevo** para registrar un evento."
                    )
                )
