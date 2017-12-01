# coding=u8
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from web_server import create_app
from web_server.ext import db

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command("server", Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0',
    port=11000)
                    )

manager.add_command("prod", Server(
    use_debugger=False,
    use_reloader=False,
    host='127.0.0.1',
    port=11000)
                    )


@manager.shell
def make_shell_context():
    return dict(app=app)


if __name__ == "__main__":
    manager.run()
    # socketio.run(app, host='0.0.0.0', port=11000, debug=True)
