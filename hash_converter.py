# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import imagehash
from requests.exceptions import ConnectionError

def convert_hash_format(filepath):
    shutil.copy(filepath, "%s.bak" % filepath)
    to_convert = open(filepath).read().splitlines()
    with open(filepath, 'w') as f:
        for line in to_convert:
            try:
                new_hash = imagehash.hex_to_hash(line)
                f.write(str(new_hash)+"\n")
                continue
            except ValueError as err:
                pass

            try:
                new_hash = imagehash.image_hash(line.strip())
                if new_hash:
                    f.write(str(new_hash)+"\n")
            except ConnectionError as err:
                pass
            except Exception as err:
                print(err)
                pass

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="file to convert")
    args = parser.parse_args()


    if args.filename:
        convert_hash_format(args.filename)


if __name__ == "__main__":
    main()