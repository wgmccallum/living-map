"""Run the Living Map API server."""

import uvicorn

uvicorn.run(
    "living_map.app:app",
    host="127.0.0.1",
    port=8000,
    reload=True,
    reload_excludes=[".venv"],
)
