from aiohttp import web


async def auth_middleware(app, handler):
    async def middleware_handler(request):
        # Check authorization header for token
        if request.method in ('POST', 'DELETE'):
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                scheme, token = auth_header.split(None, 1)
                # Just for test purpose
                if token == 'valid_token':
                    return await handler(request)
                else:
                    return web.json_response({'error': 'Unauthorized'}, status=401)
            else:
                return web.json_response({'error': 'Authorization header missing'}, status=401)
        else:
            return await handler(request)

    return middleware_handler
