from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

# ✅ Import your route modules
from routes import auth_instagram, instagram_accounts

app = FastAPI(
    title="Social Media API",
    description="An app for scheduling and responding to social media content",
    version="1.0.0",
    openapi_tags=[
        {"name": "User", "description": "User-related endpoints"},
        {"name": "Instagram Auth", "description": "Instagram OAuth endpoints"},
    ],
)

# ✅ Include routers
app.include_router(auth_instagram.router, tags=["Instagram Auth"])
app.include_router(instagram_accounts.router, tags=["Instagram Accounts"])

# ✅ Optional: Add HTTP Bearer to Swagger
security_scheme = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    openapi_schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

