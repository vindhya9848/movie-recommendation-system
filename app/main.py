from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



app = FastAPI(title="MovieBot", version="1.0")
print(">>> APP created")

# Static + templates

templates = Jinja2Templates(directory="app/ui/templates")

print(">>>  main.py Templates Ready")

app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

print(">>>  main.py static mounted")

# Routes
# from app.api import router as api_router
# app.include_router(api_router, prefix="/api")
# print(">> main.py router included")

@app.on_event("startup")
def attach_router():
    print(">>> Attaching API router")
    from app.api import router
    app.include_router(router, prefix="/api")
    print(">>> API router attached")


@app.get("/")
def home(request: Request):
    print(">>>  main.py home route called")
    return templates.TemplateResponse("index.html", {"request": request})
