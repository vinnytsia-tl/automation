import logging

import cherrypy
from cherrypy._cprequest import _cpreqbody

from app.config import Config
from app.models import UserRole

CHUNK_SIZE = 1 << 16

logger = logging.getLogger(__name__)


class AudioFiles():
    def __init__(self):
        self.template = Config.jinja_env.get_template('audio_files/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def index(self):
        files = [file.name for file in Config.audio_folder.iterdir() if file.is_file()]
        files.sort()
        return self.template.render({'files': files})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def upload(self, files: _cpreqbody.Part | list[_cpreqbody.Part]):
        files = files if isinstance(files, list) else [files]

        for part in files:
            if not part.filename or not part.file:
                logger.warning('Uploaded file has no name or content')
                continue

            with Config.audio_folder.joinpath(part.filename).open('wb') as file_out:
                logger.debug('Saving file %s', part.filename)
                while True:
                    data = part.file.read(CHUNK_SIZE)
                    if not data:
                        break
                    file_out.write(data)

        raise cherrypy.HTTPRedirect('/audio_files')
