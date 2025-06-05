from fastapi import APIRouter

from hw_status.app.routes import hw_status


app_router = APIRouter()
app_router.include_router(hw_status.router)
