import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cherrypy
from cherrypy._cprequest import _cpreqbody

from app.common.web.utils import to_query_string
from app.config import Config
from app.models import UserRole

CHUNK_SIZE = 1 << 16
FOLDER_NAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-]+$')

logger = logging.getLogger(__name__)


@dataclass
class DirEntry:
    name: str
    prefix: str
    file_callback: Optional[str]

    @property
    def url(self) -> str:
        dir_prefix = f'{self.prefix}/{self.name}' if self.prefix else self.name
        query = to_query_string({'prefix': dir_prefix, 'file_callback': self.file_callback})
        return f"/audio_files?{query}"


@dataclass
class FileEntry:
    name: str
    prefix: str
    file_callback: Optional[str]

    @property
    def url(self) -> Optional[str]:
        if self.file_callback is not None:
            file_opt = f'{self.prefix}/{self.name}' if self.prefix else self.name
            return f"{self.file_callback}&{to_query_string({'file_opt': file_opt})}"
        return None

    @property
    def has_url(self) -> bool:
        return self.file_callback is not None


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
    def index(self, prefix: str = '', file_callback: Optional[str] = None):
        prefix_list, folder = self.__handle_prefix(prefix)
        dirs, files = [], []
        for item in folder.iterdir():
            if item.is_dir():
                if FOLDER_NAME_REGEX.match(item.name):
                    dirs.append(DirEntry(item.name, prefix, file_callback))
                else:
                    logger.warning('Not listing dir %s due to bad name', item)
            else:
                files.append(FileEntry(item.name, prefix, file_callback))
        dirs.sort(key=lambda f: f.name)
        files.sort(key=lambda f: f.name)

        back_prefix = '/'.join(prefix_list[:-1]) if prefix_list else None
        query = to_query_string({'prefix': back_prefix, 'file_callback': file_callback})
        back_url = f"/audio_files?{query}"

        return self.template.render({'dirs': dirs, 'files': files, 'back_url': back_url,
                                     'prefix': prefix, 'file_callback': file_callback})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def upload_files(self, files: _cpreqbody.Part | list[_cpreqbody.Part],
                     prefix: str = '', file_callback: Optional[str] = None):
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

        raise cherrypy.HTTPRedirect('/audio_files?' + to_query_string({'prefix': prefix, 'file_callback': file_callback}))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def create_dir(self, name: str, prefix: str = '', file_callback: Optional[str] = None):
        if FOLDER_NAME_REGEX.match(name):
            _, folder = self.__handle_prefix(prefix)
            folder = folder.joinpath(name)
            logger.debug('Creating dir %s as %s', name, folder)
            folder.mkdir(exist_ok=True)
        else:
            logger.warning('Not creating dir %s due to bad name', name)
        raise cherrypy.HTTPRedirect('/audio_files?' + to_query_string({'prefix': prefix, 'file_callback': file_callback}))
