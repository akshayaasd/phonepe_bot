from fastapi import APIRouter

class GnaniRouter:
    def __init__(self, prefix=""):
        self.router = APIRouter(prefix=prefix)

    def get(self, path, **kwargs):
        return self.router.get(path, **kwargs)

    def post(self, path, **kwargs):
        return self.router.post(path, **kwargs)

    def put(self, path, **kwargs):
        return self.router.put(path, **kwargs)

    def delete(self, path, **kwargs):
        return self.router.delete(path, **kwargs)