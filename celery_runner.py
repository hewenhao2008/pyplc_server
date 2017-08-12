import os
from web_server import create_app
from celery import Celery
from web_server.tasks import test, check_station


def make_celery(app):
    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_BACKEND_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


env = os.environ.get('WEBAPP_ENV', 'dev')
flask_app = create_app('webapp.config.%sConfig'.format(env.capitalize()))
celery = make_celery(flask_app)
