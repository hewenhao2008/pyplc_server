import time
from os import path

from flask import current_app, Blueprint
from web_server.models import db, YjStationInfo, TransferLog

task_blueprint = Blueprint(
    'task',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'task'),
    url_prefix='/task'
)


@task_blueprint.route('/test', methods=['GET'])
def test():
    print(current_app.config['VARIABLE_COUNT'])
    print('this is task crontab.')
    return 'test'


@task_blueprint.route('/check_station', methods=['GET'])
def check_station():
    with current_app.app_context():
        current_time = int(time.time())
        stations = db.session.query(YjStationInfo)
        for s in stations:
            last_log = s.logs.order_by(TransferLog.time.desc()).first()
            if last_log:
                last_time = last_log.time
                last_level = last_log.level
                if current_time - last_time > current_app.config.STATION_TIMEOUT:
                    warn_level = last_level + 1
                    if warn_level >= 3:
                        level = 3
                        note = 'ERROR'
                    else:
                        level = warn_level
                        note = 'WARNING'
                else:
                    level = 0
                    note = 'OK'
            else:
                level = 0
                note = 'First Check'

            warn = TransferLog(
                station_id=s.id,
                level=level,
                time=current_time,
                note=note
            )
            db.session.add(warn)
        db.session.commit()
    return 'check station complete.'
