import fnmatch
import json
import os
import sys

from binaryornot.check import is_binary


DEFAULT_WORDS = ['FIXME', 'TODO', 'HAX', 'HACK', 'XXX']


def normalize_paths(paths):
    return [p.lstrip('/') for p in paths]


def parse_config():
    with open('/engine_config.json', 'r') as fd:
        engine_config = json.loads(fd.read())
        include_paths = normalize_paths(engine_config.get('include_paths', []))
        exclude_paths = normalize_paths(engine_config.get('exclude_paths', []))
    return include_paths, exclude_paths


def _should_include_path(path, include_paths, exclude_paths):
    # First check if there are include paths
    if include_paths:
        for i_path in include_paths:
            if fnmatch.fnmatch(path, i_path):
                return True
        return False

    # Check exclude paths
    for e_path in exclude_paths:
        if fnmatch.fnmatch(path, e_path):
            return False
    return True


def _report_line(file_path, line_number, word):
    print(json.dumps({
        'name': 'line containing "{}"'.format(word),
        'description': 'Your settings are set to point out lines with the term "{}"'.format(word),
        'location': {
            'path': file_path,
            'line': line_number
        }
    }))


def search_file(patterns, file_path):
    # Don't search binary files
    if is_binary(file_path):
        return

    # Make sure the file is less than 1 MB
    try:
        if os.stat(file_path).st_size > 1024 * 1024:
            return
    except IOError:
        # If we are for some reason unable to stat this file, then we probably won't be able to read it either
        return

    try:
        with open(file_path, 'r') as fd:
            for line_number, line in enumerate(fd, 1):
                if len(line) > 1000:
                    # only allow lines less than 1000 characters, since greater than this is likely not source code
                    continue

                for pattern in patterns:
                    if pattern in line:
                        _report_line(file_path, line_number, line)
                        break

    except (ValueError, IOError):
        pass


def main():
    patterns = []
    for word in DEFAULT_WORDS:
        patterns.append(word.upper())
        #patterns.append(word.lower())
        #patterns.append(word.title())

    include_paths, exclude_paths = parse_config()

    # Add the .git path to excludes since there are a bunch of text files
    exclude_paths.append('.git/*')

    for root, dirs, files in os.walk('.'):
        root_dir = os.path.normpath(root)
        for f in files:
            path = os.path.join(root_dir, f)
            if not _should_include_path(path, include_paths, exclude_paths):
                continue
            search_file(patterns, path)


if __name__ == '__main__':
    args = sys.argv[1:]
    main()
