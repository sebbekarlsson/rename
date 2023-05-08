import argparse
from rename.utils import rename_project


def run():
    parser = argparse.ArgumentParser(description='Rename an entire code base.')
    parser.add_argument('path', type=str, help='Path to directory of code base')
    parser.add_argument('old_name', type=str, help='Old name')
    parser.add_argument('new_name', type=str, help='New name')
    parser.add_argument('-d', help='Dry run', default=False, required=False, action='store_true')
    args = parser.parse_args()

    rename_project(args.path, args.old_name, args.new_name, args.d)
