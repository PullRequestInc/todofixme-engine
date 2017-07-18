import json
import os
import subprocess
import sys

WORDS = ['FIXME', 'TODO', 'HAX', 'HACK', 'XXX']


def parse_and_print_results(result_text):
    for line in result_text.splitlines():
        split_parts = line.split(':')
        if len(split_parts) != 3:
            # Unexpected output
            continue
        path, line_number, word = split_parts
        print(json.dumps({
            'name': 'comment with "{}"'.format(word),
            'description': 'Your settings are set to point out comments with the term "{}"'.format(word),
            'location': {
                'path': os.path.normpath(path),
                'start': {
                    'line': line_number
                },
                'end': {
                    'line': line_number
                }
            }
        }))


def main():
    try:
        output = subprocess.check_output([
            'grep',
            '--binary-files=without-match',
            '--only-matching',
            '--with-filename',
            '--extended-regexp',
            '-rn',
            '({})'.format('|'.join(WORDS)),
            '.']
        )
        parse_and_print_results(output.decode().strip())
    except subprocess.CalledProcessError as exc:
        # No matches found
        pass


if __name__ == '__main__':
    args = sys.argv[1:]
    main()
