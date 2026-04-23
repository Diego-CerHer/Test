from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, ConversationState, MemoryStorage
from botbuilder.schema import Activity
from bot import BotIncidentes
from dialogs.reporte_dialog import ReporteDialog
from storage.database import inicializar_db
import config
import json

inicializar_db()

settings = BotFrameworkAdapterSettings(config.APP_ID, config.APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)

memory = MemoryStorage()
conversation_state = ConversationState(memory)

dialog = ReporteDialog()
bot = BotIncidentes(conversation_state, dialog)


async def messages(req: Request) -> Response:
    if req.content_type != "application/json":
        return Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return Response(status=201)


app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=config.PORT)
