from gnani_sdk.router import GnaniRouter
from gnani_sdk.logging import setup_logger

logger = setup_logger("default_routes")
router = GnaniRouter(prefix="/health").router

@router.get("/livecheck")
def livecheck():
    return {"ok": True}

@router.get("/readycheck")
def readycheck():
    return {"ok": True}