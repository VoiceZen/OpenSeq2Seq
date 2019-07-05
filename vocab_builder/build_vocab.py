"""Build vocabulary from manifest files.

Each item in vocabulary file is a character.
"""
import argparse
import functools
import codecs
import json
from collections import Counter
import os.path
import pandas as pd
from utility import add_arguments, print_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
# yapf: disable
add_arg('count_threshold',  int,    0,  "Truncation threshold for char counts.")
add_arg('vocab_path',       str,
        'data/librispeech/vocab.txt',
        "Filepath to write the vocabulary.")
add_arg('manifest_paths',   str,
        None,
        "Filepaths of manifests for building vocabulary. "
        "You can provide multiple manifest files.",
        nargs='+',
        required=True)
add_arg('file_type',   str,
        'csv',
        "File type of manifests for building vocabulary. ")
# yapf: disable
args = parser.parse_args()

def read_manifest(
    manifest_path,
    max_duration=float('inf'),
    min_duration=0.0,
    type='csv'
):
    """Load and parse manifest file.

    Instances with durations outside [min_duration, max_duration] will be
    filtered out.

    :param manifest_path: Manifest file to load and parse.
    :type manifest_path: basestring
    :param max_duration: Maximal duration in seconds for instance filter.
    :type max_duration: float
    :param min_duration: Minimal duration in seconds for instance filter.
    :type min_duration: float
    :return: Manifest parsing results. List of dict.
    :rtype: list
    :raises IOError: If failed to parse the manifest.
    """
    if type == 'json':
        manifest = []
        for json_line in codecs.open(manifest_path, 'r', 'utf-8'):
            try:
                json_data = json.loads(json_line)
            except Exception as e:
                raise IOError("Error reading manifest: %s" % str(e))
            if (json_data["duration"] <= max_duration and
                    json_data["duration"] >= min_duration):
                manifest.append(json_data)
        return manifest
    else:
        columns = ['audio_filepath', 'duration', 'text']
        df = pd.read_csv(manifest_path, names=columns,sep=";",skiprows=1)
        # import pdb; pdb.set_trace();
        df = df[df['duration'].between(min_duration, max_duration, inclusive=True)]
        return df.T.to_dict().values()

def count_manifest(counter, manifest_path):
    manifests = read_manifest(manifest_path, type=args.file_type)    
    for line in manifests:
        try:
            for char in line['text']:
                if char == "\x9f":
                    print(char)
                counter.update(char)
        except:
            print(char)
            #pass
            # import pdb; pdb.set_trace()


def main():
    print_arguments(args)

    counter = Counter()
    for manifest_path in args.manifest_paths:
        count_manifest(counter, manifest_path)

    count_sorted = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    with codecs.open(args.vocab_path, 'w', 'utf-8') as fout:
        for char, count in count_sorted:
            if count < args.count_threshold: break
            try:
                fout.write(char + '\n')
            except:
                # pass
                import pdb; pdb.set_trace()


if __name__ == '__main__':
    main()
