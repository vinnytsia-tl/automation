import logging
import re
from pathlib import Path

import cherrypy
from cherrypy._cprequest import _cpreqbody

from app.config import Config
from app.models import UserRole

CHUNK_SIZE = 1 << 16
FOLDER_NAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-]+$')

logger = logging.getLogger(__name__)


class AudioFiles():
    def __init__(self):
        self.template = Config.jinja_env.get_template('audio_files/index.html')

    def __handle_prefix(self, prefix: str) -> tuple[list[str], Path]:
        prefix_list = list(filter(FOLDER_NAME_REGEX.match, prefix.split('/')))
        folder = Config.audio_folder.joinpath(*prefix_list)
        if not folder.is_dir():
            raise cherrypy.HTTPRedirect('/audio_files')
        return prefix_list, folder

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.RUNNER)
    def index(self, prefix: str = ''):
        prefix_list, folder = self.__handle_prefix(prefix)
        dirs, files = [], []
        for item in folder.iterdir():
            if item.is_dir():
                if FOLDER_NAME_REGEX.match(item.name):
                    dirs.append({'name': item.name, 'prefix': f'{prefix}/{item.name}' if prefix else item.name})
                else:
                    logger.warning('Not listing dir %s due to bad name', item)
            else:
                files.append({'name': item.name})
        dirs.sort(key=lambda f: f['name'])
        files.sort(key=lambda f: f['name'])
        back_prefix = '/'.join(prefix_list[:-1]) if prefix_list else None
        return self.template.render({'dirs': dirs, 'files': files, 'back_prefix': back_prefix, 'prefix': prefix})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def upload_files(self, files: _cpreqbody.Part | list[_cpreqbody.Part], prefix: str = ''):
        files = files if isinstance(files, list) else [files]
        _, folder = self.__handle_prefix(prefix)

        for part in files:
            if not part.filename or not part.file:
                logger.warning('Uploaded file has no name or content')
                continue

            path = folder.joinpath(part.filename).resolve()
            if not path.parent.samefile(folder):
                logger.warning('Uploaded file has bad name')
                continue

            logger.debug('Saving file %s to %s', part.filename, path)

            with path.open('wb') as file_out:
                while True:
                    data = part.file.read(CHUNK_SIZE)
                    if not data:
                        break
                    file_out.write(data)

        raise cherrypy.HTTPRedirect('/audio_files?prefix=' + prefix)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def create_dir(self, name: str, prefix: str = ''):
        if FOLDER_NAME_REGEX.match(name):
            _, folder = self.__handle_prefix(prefix)
            folder = folder.joinpath(name)
            logger.debug('Creating dir %s as %s', name, folder)
            folder.mkdir(exist_ok=True)
        else:
            logger.warning('Not creating dir %s due to bad name', name)
        raise cherrypy.HTTPRedirect('/audio_files?prefix=' + prefix)
