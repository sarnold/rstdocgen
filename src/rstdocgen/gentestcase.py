""""
Simple testcase generator using default procedure template.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

from munch import Munch
from yaml_tools.utils import load_config, process_template

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

VERSION = version('rstdocgen')

# map of ID prefix to name for categories of test cases.
#   type setup goes with STD doc Cha 3 Test Preparations
#   type performance goes with STD doc Cha 4 Test Descriptions
# 3) setup cases are prerequisites to 4) test cases.
# setup cases may also include initial data collection for later test cases.
# the mapped name is used for the folder name under OUT_PATH/tests.
PREFIX_MAP = {
    "PT": "performance",
    "ST": "security",
    "SU": "setup",
}


def dir_from_name(name: str, opts: Dict, debug: bool):
    """
    Get the subdir name from test case ID.
    """
    keyname = name.partition(opts["id_sep"])[0]
    dirname = PREFIX_MAP[keyname]
    if debug:
        print(f"key, dirname: {keyname}, {dirname}")
    return dirname


def create_outyaml(data: str, context: Path, opts: Dict, debug: bool):
    """
    Construct the testcase filename and write out processed data.
    """
    doc = Munch.fromYAML(data)
    out_name = f'{doc.id}-{context.stem}.yaml'
    print(f"Got test data for {doc.id}")
    dir_name = dir_from_name(out_name, opts, debug)
    out_dir = Path(opts["output_path"]) / dir_name
    if debug:
        print(f"Target dir is {out_dir}")
    out_file = out_dir / out_name
    out_file.write_text(data, opts["file_encoding"])
    print(f"New testcase written to {str(out_file)}")


def process_inputs(filearg: str, opts: Dict, debug: bool):
    """
    Process input data file+template and create YAML test case source.
    """
    context_data = Path(filearg)
    template_yaml = Path(opts["template_path"]) / opts["template_file"]
    out_str = process_template(template_yaml, context_data, opts)
    if debug:
        print(out_str)
    create_outyaml(out_str, context_data, opts, debug)


def main(argv=None):  # pragma: no cover
    """
    Turn YAML context data into DID-like test description metadata (see
    section 4.x.y in System/Software Test Description DID).
    """
    debug = False
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=''''Generate RST test case from YAML source(s).
            Either provide a single source file as the last argument
            or use the ``--file-glob`` argument to search under the
            path provided by the ``source_path`` key in the config
            file.''',
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display more processing info",
    )
    parser.add_argument(
        '-d',
        '--dump-config',
        action='store_true',
        dest="dump",
        help='Dump default configuration file to stdout',
    )
    parser.add_argument(
        '-s',
        '--save-config',
        action='store_true',
        dest="save",
        help='Save active config to default filename (.genrstdocs.yml) and exit',
    )
    parser.add_argument(
        'file',
        nargs='*',
        metavar="FILE",
        type=str,
        help="Process input file(s) to target directory",
    )

    args = parser.parse_args()

    self_name = Path(__file__).stem
    cfg, pfile = load_config(self_name)
    popts = Munch.toDict(cfg)
    outdir = popts['output_path']

    if args.save:
        cfg_data = pfile.read_bytes()
        def_config = Path(f'.{self_name}.yml')
        def_config.write_bytes(cfg_data)
        sys.exit(0)
    if args.dump:
        sys.stdout.write(pfile.read_text(encoding=popts['file_encoding']))
        sys.exit(0)
    if args.verbose:
        debug = True
    if not args.file:
        parser.print_help()
        sys.exit(1)
    if debug:
        print(f'Creating output directory {outdir}')
    Path(outdir).mkdir(exist_ok=True)
    for filearg in args.file:
        process_inputs(filearg, popts, debug)


if __name__ == '__main__':
    main()
