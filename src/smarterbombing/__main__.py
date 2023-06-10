"""Main application entrypoint"""
from argparse import ArgumentParser
import sys

import smarterbombing.webui.ui as ui

parser = ArgumentParser(
    prog='smarterbombing',
    description='Parse Eve Online combat logs and display statistics.',
    epilog='Show your support by sending ISK in-game to Ageliten.')

MODE_HELP = 'How to run smarterbombing -- webui (default)'
PORT_HELP = 'Which port to use for hosting the webui.'

parser.add_argument(
    '--mode',
    default='webui',
    required=False,
    help=MODE_HELP)

parser.add_argument(
    '--port',
    default=42069,
    required=False,
    help=PORT_HELP
)

args = parser.parse_args()

if args.mode == 'webui':
    print('Starting WebUI...')
    ui.run_webui(args.port)
else:
    print(f'unrecognized mode: {args.mode}')
    sys.exit(1)
