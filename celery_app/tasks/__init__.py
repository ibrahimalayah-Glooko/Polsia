from celery_app.tasks import (  # noqa: F401 -- registers @app.task functions
    agent_tasks,
    daily_cycle,
    maintenance,
)
