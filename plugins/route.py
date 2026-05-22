from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def health(request):
    return web.json_response({"status": "ok", "service": "File-Sharing-Bot"})
