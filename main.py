from fastapi import FastAPI
from db import createDBandTables
from auth import router as auth_router
from fastapi.openapi.utils import get_openapi
from routes.accounts import router as accounts_router

app = FastAPI()

@app.get("/startingup")
def func():
    return("hello world")

@app.on_event("startup")
def onStartup():
    createDBandTables()

app.include_router(auth_router)
app.include_router(accounts_router)

def customOpenAPI():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema =get_openapi(
        title= "Todo App",
        version= "1.0.0",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type" : "http",
            "scheme" : "Bearer",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = customOpenAPI