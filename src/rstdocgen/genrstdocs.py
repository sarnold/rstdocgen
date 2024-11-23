#!/usr/bin/env python3
"""
Simple rst doc generator using yaml doc inputs and rstobjs.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

from munch import Munch
from rstobj import directives, markup

from yaml_tools.utils import get_filelist, load_config, text_file_reader

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

VERSION = version('rstdocgen')


def inc_from_name(fname: str, opts: Dict, debug: bool) -> str:
    """
    Get the include filename from test case filename.
    """
    inc_file = ''
    test, num, _ = fname.split(opts["id_sep"], maxsplit=2)
    if debug:
        print(f"test, num: {test}, {num}")
    _, sub_num, _ = num.split(".")
    if test == "SU":
        inc_file = f"includes/test_prep_{sub_num}.rst"
    elif test in ["PT", "ST"]:
        inc_file = f"includes/test_desc_{sub_num}.rst"
    if debug:
        print(f"Include name: {inc_file}")
    return inc_file


def append_include(infile: Path, opts: Dict, debug: bool):
    """
    Append a new include directive for rst testcase.
    """
    page_break = opts["page_break"]
    inc_str = inc_from_name(infile.name, opts, debug)
    inc_path = f"../tests/{infile.name}"
    inc = directives.miscellaneous.Include(path=inc_path)
    append_text = f"\n{inc.render()}\n{page_break}"
    inc_file = Path('std') / inc_str
    if debug:
        print(f"Include file for writing: {inc_file}")
    inc_text = inc_file.read_text()
    if infile.name not in inc_text:
        inc_text = inc_text + append_text
        inc_file.write_text(inc_text, opts["file_encoding"])
        print(f"New include written to {str(inc_file)}")


def create_docstr(data: Dict, opts: Dict) -> str:
    """
    Format the testcase data as rst string chunks.
    """
    chunks = []
    is_analysis = False
    mdata = Munch.fromDict(data)
    page_break = opts["page_break"]

    # title header does not fit well in the hierarchy
    title_str = f"{mdata.title}"  # level 2 is actually 3
    header1 = markup.Header(title=title_str, header_level=2, auto_label=False)
    chunks.append(header1.render())
    docid = f':ID: {mdata.id}'
    title = f':Title: {mdata.title}'
    purpose = f':Purpose: {mdata.purpose}'
    desc = f':Description: {mdata.description}'
    chunks.append(f"\n{docid}\n{title}\n{purpose}\n{desc}\n")

    # make a field list for requirement IDs
    if "reqs" in data:
        hdr2_str = f"Requirements for {mdata.title}"
        header2 = markup.Header(title=hdr2_str, header_level=4, auto_label=False)
        chunks.append(header2.render())
        rfield_list = "\n"
        for req in mdata.reqs:
            rfield_list += f':{req.id}: {req.method}\n'
            if req.method == 'A':
                is_analysis = True
        chunks.append(rfield_list)
    else:
        chunks.append("\nRequirements: None")

    # STD DID metadata sections are text blocks with optional formatting
    strings = ["Prerequisites", "Inputs", "Expected Results", "Assumptions and Constraints"]  # fmt: skip
    blobs = [mdata.prereqs, mdata.inputs, mdata.expected_results, mdata.assumptions_constraints]  # fmt: skip
    for string, blob in zip(strings, blobs):
        hdr_str = f"{string} for {mdata.title}"
        hdr_obj = markup.Header(title=hdr_str, header_level=4, auto_label=False)
        chunks.append(hdr_obj.render() + "\n")
        chunks.append(blob)

    # procedures start with a header
    if is_analysis:
        proc_str = f"Analysis procedures for {mdata.title}"
    else:
        proc_str = f"{page_break}\nProcedures for {mdata.title}"
    proc_hdr = markup.Header(title=proc_str, header_level=4, auto_label=False)
    chunks.append(proc_hdr.render() + "\n")

    # finally make a steps table
    sdata: List = [[] for i in range(len(mdata.steps) + 1)]
    act_str = "Action"
    res_str = "Expected Result"
    step_hdr = ["Step", act_str, res_str]
    not_steps = ["note", "verif"]
    sdata[0].extend(step_hdr)

    count = 0
    for idx, step in enumerate(mdata.steps, 1):
        if isinstance(step.Step, str) and step.Step.lower() in not_steps:
            step_text = step.Step
            count += 1
        else:
            step_text = str(idx - count)
        if step[res_str] == '':
            step[res_str] = '|'
        row = [step_text, step[act_str], step[res_str]]
        sdata[idx].extend(row)

    stable = directives.ListTable(
        data=sdata, title="Steps and Notes", header=True, widths=[6, 44, 22]
    )
    chunks.append(stable.render())

    return '\n'.join(chunks)


def create_outrst(data: str, infile: Path, opts: Dict, debug: bool):
    """
    Construct the testcase filename and write out processed rst data.
    """
    out_name = f'{infile.stem}.rst'
    print(f"Got test data for {infile.name}")
    out_file = Path(opts["output_path"]) / out_name
    out_file.write_text(data, opts["file_encoding"])
    print(f"New testcase written to {str(out_file)}")
    append_include(out_file, opts, debug)


def process_inputs(file, popts, debug):
    """
    Process YAML test case source to create RST test case file.
    """
    pfile = Path(file)
    out_dict = text_file_reader(file, popts)
    docstr = create_docstr(out_dict, popts)
    # print(docstr)
    create_outrst(docstr, pfile, popts, debug)


def main(argv=None):  # pragma: no cover
    """
    Turn YAML test case sources into DID-like test cases with procedures
    and metadata (see section 4.x.y in System/Software Test Description
    DID).
    """
    debug = False
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Generate RST test case doc(s) from YAML source',
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
        help='save active config to default filename (.gentestcase.yml) and exit',
    )
    parser.add_argument(
        '-f',
        '--file-glob',
        action='store_true',
        dest="glob",
        help='Find all source files via glob ',
    )
    parser.add_argument(
        'file',
        nargs='?',
        metavar="FILE",
        type=str,
        help="Name of single source file",
    )

    args = parser.parse_args()

    pkg_path = 'rstdocgen.data'
    self_name = Path(__file__).stem
    cfg, pfile = load_config(self_name, pkg_path)
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
    if not args.file and not args.glob:
        parser.print_help()
        sys.exit(1)
    if debug:
        print(f'Creating output directory {outdir}')
    Path(outdir).mkdir(exist_ok=True)

    file_glob = get_filelist(popts["source_path"], popts["file_glob"], debug)
    files = file_glob if args.glob else [args.file]
    if debug:
        print(files)
    for filearg in files:
        process_inputs(filearg, popts, debug)


if __name__ == '__main__':
    main()
