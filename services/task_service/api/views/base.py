import json

import aiohttp_cors
from aiohttp import web

from api.exceptions import WrongBodyFormatException
from api.utils.annotations import DictStrAny

__all__ = [
    "BaseView",
    "BaseListView",
]


class BaseView(web.View, aiohttp_cors.CorsViewMixin):
    async def _get_data(self) -> DictStrAny:
        try:
            return await self.request.json()
        except json.decoder.JSONDecodeError as e:
            raise WrongBodyFormatException("Invalid JSON in request") from e

    async def _get_form_data(self) -> DictStrAny:
        return await self.request.post()


class BaseListView(BaseView):
    pass
