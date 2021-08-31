import os
import json
import subprocess

if not os.path.isdir('input') or not os.path.isdir('output'):
    raise ValueError('Required directories: input, output')

_, _, filenames = next(os.walk('input'))
filenames = [name[:-8] for name in filenames if name.endswith('-in.json')]


def json_list_to_set(json):
    if isinstance(json, list):
        return frozenset(map(lambda e: json_list_to_set(e), json))
    if isinstance(json, dict):
        return {k: json_list_to_set(v) for k, v in json.items()}
    return json


for filename in filenames:
    pipe = subprocess.Popen(['../../src/testRoom'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    with open(os.path.join('input', filename + '-in.json')) as in_file:
        actual_stdout = json.loads(pipe.communicate(input=in_file.read().encode())[0].decode())
        try:
            with open(os.path.join('output', filename + '-out.json')) as out_file:
                expected_stdout = json.loads(out_file.read())
        except FileNotFoundError:
            print(f'Expected output file {filename}-out.json')
            continue

    try:
        assert json_list_to_set(actual_stdout) == json_list_to_set(expected_stdout)
        print(f'File {filename}-in.json / {filename}-out.json passed')
    except AssertionError:
        print(f'File {filename}-in.json / {filename}-out.json failed')
