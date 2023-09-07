import os
import os.path as path
import re
import sys
import urllib.parse as parser
from typing import Callable, TypeAlias, Iterable
from playwright.sync_api import PlaywrightContextManager, sync_playwright
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
fprint = Console().print
PosixPath: TypeAlias = str
DIR = '/Users/alan/gitproj/website/docs'
OUT_DIRNAME = 'i18n'
EXT = '.md'
# DIRNAMES =  [x.strip() for x in  os.getenv('exclude_dirs').split(',') if x.strip()]
DIRNAMES = [
    # 'tutorials',
    # 'guides',
    # 'controls',
    'cli',
]

EXCLUDE_REGEX = os.getenv('exclude_regex') or (DIRNAMES and r'|'.join(DIRNAMES)) or '?'
BrowserInstance = None
DOC_PATH = os.getenv('doc_folder')


def getBrowser() -> PlaywrightContextManager:
    global BrowserInstance
    if not BrowserInstance:
        BrowserInstance = sync_playwright()
    return BrowserInstance


def setAndGetUrl(translate_text: str = '') -> str:
    base_url = 'https://translate.google.com/'
    text = parser.quote(translate_text)
    if text == '':
        return base_url
    return f'{base_url}?sl=auto&tl=zh-CN&text={text}&op=translate'


def setNewPath(current_path: PosixPath = DOC_PATH):
    if not current_path:
        fprint('Document path needs to be specified!')
        exit(0)
    # current_dirname = path.dirname(DIR), # TODO: Has bug
    current_basename = path.basename(DIR)
    new_path = path.join(
        path.join(
            # current_dirname,
            OUT_DIRNAME,
            current_basename,
        ),
        current_path.replace(DIR, '').strip('/'),
    )

    # Create a file parent directory
    new_dir = new_path.replace(path.basename(new_path), '').strip('/')
    if not path.exists(new_dir):
        os.makedirs(new_dir)
    return new_path


def filterInvalidItems(array: Iterable):
    return [x for x in array if str(x).strip()]


def filterItems(array: Iterable[str]):
    return [x.strip() for x in array if x.strip()]


def endswith(exclude_regex=EXCLUDE_REGEX):
    filePaths = []
    for parent, _, files in os.walk(path.abspath(DIR)):
        if re.search(exclude_regex, parent):
            continue
        for f in files:
            if (realPath := path.join(parent, f)).endswith(EXT):
                filePaths.append(realPath)
    return sorted(filePaths)


def sysHasArgs(*args: Iterable[str]):
    for arg in args:
        if arg in sys.argv[1:]:
            return True
    return False


def getSelected() -> int | str | tuple:
    argvs = sys.argv[1:]
    if argvs and '-a' in argvs:
        return 'all'

    def isNum(nu: str):
        return nu.isdigit() or (nu[:1] == '-' and nu[1:].isdigit())

    for i, argv in enumerate(argvs):
        if sysHasArgs('-c', '--count'):
            return 'view'
        if i != len(argvs) - 1:
            if sysHasArgs('-s', '--select'):
                i1 = argvs[i + 1]
                if isNum(i1):
                    return int(i1)
                if i1 == 'all':
                    return 'all'
            elif sysHasArgs('-ss', '-sm', '--select-multiple'):
                return tuple([int(x) for x in argvs[i + 1 :]])  # noqa
            elif sysHasArgs('--head'):
                i1 = argvs[i + 1]
                if isNum(i1):
                    return ('head', int(i1))
            elif sysHasArgs('--tail'):
                i1 = argvs[i + 1]
                if isNum(i1):
                    return ('tail', int(i1))
    return 'null'


def add_data(*filePaths, before: Callable = None, after: Callable = None):
    def wrapper(func):
        def inner(*args, **kw):
            if len(args) > 1:
                import logging

                logging.warning('(args[1:])The following parameters will be discarded')
            for fp in filePaths:
                if isinstance(before, Callable):
                    before(fp)
                func(args[0], *fp, **kw)
                if isinstance(after, Callable):
                    after(fp)

        return inner

    return wrapper


def init(filePaths: list = []) -> list[tuple[str, str]]:
    filePaths = filePaths or endswith()
    paths = []
    selected = getSelected()
    if selected:
        fprint('getArgs:', type(selected), selected)
        if selected == 'all':
            paths = filePaths
        elif selected == 'view':
            fprint([(i, v) for i, v in enumerate(filePaths)])
            exit(0)
        elif isinstance(selected, int):
            fprint(0)
            if selected >= 0 and selected < len(filePaths):
                paths = filePaths[selected : selected + 1]  # noqa
            if selected < 0 and abs(selected) < len(filePaths):
                paths = [filePaths[selected]]  # noqa
        elif isinstance(selected, tuple):
            if len(selected) == 2:
                s1, s2 = selected
                if s1 == 'head':
                    if s2 >= 0 and s2 < len(filePaths):
                        paths = filePaths[:s2]
                    else:
                        fprint(f'erro: {s1} {s2} > 0')
                elif s1 == 'tail' and s2 < 0 and abs(s2) < len(filePaths):
                    paths = filePaths[s2:]
                else:
                    fprint(f'error: {s1} {s2} < 0')
            else:
                paths = []
                for i in selected:
                    if str(i).isdigit() and int(i) < len(filePaths):
                        paths.append(filePaths[i])

        elif selected == 'null':
            paths = []

        if paths and paths != filePaths:
            fprint([{filePaths.index(p): p} for p in paths])
        if not paths:
            fprint('filePaths:\n    Use -c to view id map of filePaths')
            exit(0)
        if paths:
            paths = [(filePaths.index(v), v) for v in paths]
    return paths


if __name__ == '__main__':
    # test function
    fprint(sysHasArgs('-a'))
    fprint(getSelected())
