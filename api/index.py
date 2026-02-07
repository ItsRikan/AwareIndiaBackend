from src.api.index import app

# This file is a thin adapter so Vercel finds a Serverless Function
# inside the top-level `api/` directory. Vercel's Python runtime
# will use the `app` ASGI application exported above.
