import sys
import os
import os.path
import pkgutil
import importlib
import argparse
import traceback
import importlib.util
import configparser
from scenario import __version__
from scenario import fixture

RUNNING = '\033[0;34mRUNNING\033[0m'
DONE = '\033[0;32mDONE\033[0m'
FAIL = '\033[0;31mFAIL\033[0m'


def _load_module_info(module_info):
    spec = module_info.module_finder.find_spec(module_info.name)
    return spec.loader.load_module()


def _load_fixture(path, host, token):
    setattr(fixture, 'HOST', host)
    setattr(fixture, 'TOKEN', token)

    _fixture = fixture

    # load fixture extension
    fixture_infos = list(filter(
        lambda x: x.name == 'fixture',
        pkgutil.walk_packages([path])
    ))
    if len(fixture_infos) == 1:
        fixture_info = fixture_infos[0]
        _fixture = _load_module_info(fixture_info)

        # override fixture
        for ext_name in dir(fixture):
            if ext_name.startswith('__'):
                continue

            ext = getattr(fixture, ext_name)
            setattr(_fixture, ext_name, ext)

    return _fixture


def run_scenraio(host, token, targets=None):
    cwd = os.getcwd()
    _fixture = _load_fixture(cwd, host, token)
    submodules = pkgutil.iter_modules([cwd])
    print('Run scenarios in local server\n')

    for module in submodules:
        if targets is not None and len(targets) != 0:
            if module.name not in targets:
                continue
        scenario = _load_module_info(module)
        try:
            print(f'* {module.name} .......................... [{RUNNING}]')
            scenario.test(_fixture)
            print(f'* {module.name} .......................... [{DONE}]')
        except Exception as e:
            print(f'* {module.name} .......................... [{FAIL}]')
            print(f'Message: {e}')
            traceback.print_exc()


def list_scenario():
    cwd = os.getcwd()
    submodules = pkgutil.iter_modules([cwd])
    for module in submodules:
        if module.name == 'fixture':
            continue
        print(module.name)


def main(arg_parser, config_parser):
    args = arg_parser.parse_args()
    environ = args.environment
    host, token = None, None

    try:
        config = config_parser[environ]
        host = config['Host']
        token = config['Token'].strip()
    except KeyError:
        print('Invalid enviroment')
        sys.exit(-1)

    if args.list:
        list_scenario()
    elif args.all:
        run_scenraio(host, token, None)
    elif len(args.targets) != 0:
        run_scenraio(host, token, args.targets)
    else:
        print('Please specify test target or flag running all test')
        arg_parser.print_help()
        sys.exit(-1)



if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog='scenario',
        description='Process some integers.'
    )

    arg_parser.add_argument('targets', metavar='target', type=str, nargs='*',
                        help='specify scenario target')
    arg_parser.add_argument('-l', '--list', action="store_true",
                        help='list all scenario')
    arg_parser.add_argument('--all', action="store_true",
                        help='Run all scenario')
    arg_parser.add_argument('-v', '--version',
                        action='version', version=f'%(prog)s {__version__}')
    arg_parser.add_argument('-e', '--environment', type=str,
                        default="DEFAULT", help='test environment')

    config_parser = configparser.ConfigParser()
    config_parser.read(os.path.join(os.getcwd(), 'config.ini'))

    main(arg_parser, config_parser)
