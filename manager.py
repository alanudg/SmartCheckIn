import app.config as config
from flask_apidoc.commands import GenerateApiDoc
from flask_script import Manager

manager = Manager(config.app)
manager.add_command('apidoc', GenerateApiDoc(input_path='app/api',
                                             output_path='app/static/docs'))

if __name__ == "__main__":
    manager.run()
