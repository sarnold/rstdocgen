#!/usr/bin/env python3
"""
Simple converter check.
"""
import os

from yaml_tools.utils import text_data_writer, text_file_reader

OPTS = {
    'file_encoding': 'utf-8',
    'output_format': 'yaml',
    'default_csv_hdr': None,
    'csv_delimiter': ';',
    'preserve_quotes': False,
    'mapping': 4,
    'sequence': 6,
    'offset': 4,
}


FILE = os.getenv('IN_FILE', default='resources/GS/pwrup.csv')
# read in some csv "column data"
data = text_file_reader(FILE, OPTS)
# spit out some yaml
text_data_writer(data, OPTS)
