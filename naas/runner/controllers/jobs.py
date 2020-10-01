from sanic.views import HTTPMethodView
from sanic import response
from naas.types import t_asset, t_job, t_error
import uuid


class JobsController(HTTPMethodView):
    __jobs = None
    __logger = None

    def __init__(self, logger, jobs, *args, **kwargs):
        super(JobsController, self).__init__(*args, **kwargs)
        self.__jobs = jobs
        self.__logger = logger

    async def get(self, request):
        uid = str(uuid.uuid4())
        status = await self.__jobs.list(uid)
        self.__logger.info(
            {"id": uid, "type": t_asset, "status": "send", "filepath": "status"}
        )
        return response.json(status)

    async def post(self, request):
        uid = str(uuid.uuid4())
        data = request.json
        if (
            not data
            or list(["path", "type", "params", "value", "status"]).sort()
            != list(data.keys()).sort()
        ):
            self.__logger.info(
                {
                    "id": uid,
                    "type": t_job,
                    "status": t_error,
                    "error": "missing keys",
                    "tb": data,
                }
            )
            return response.json({"result": "missing keys"}, status=400)
        updated = await self.__jobs.update(
            uid,
            data["path"],
            data["type"],
            data["value"],
            data["params"],
            data["status"],
        )
        if updated.get("error"):
            return response.json(updated, status=409)
        self.__logger.info({"id": uid, "type": t_job, "status": updated["status"]})
        return response.json(updated)
