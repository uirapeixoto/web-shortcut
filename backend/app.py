from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.auth import router as auth_router, get_current_user
from routes.categories import router as cat_router
from routes.shortcuts import router as sc_router
from routes.ebooks import router as ebook_router

app = FastAPI(title="Web Shortcut Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

init_db()

# Auth is public — all other routers require a valid session cookie
app.include_router(auth_router)
app.include_router(cat_router,   dependencies=[Depends(get_current_user)])
app.include_router(sc_router,    dependencies=[Depends(get_current_user)])
app.include_router(ebook_router, dependencies=[Depends(get_current_user)])
