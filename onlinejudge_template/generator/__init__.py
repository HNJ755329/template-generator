import pathlib
from typing import *

import appdirs
import mako.lookup
import mako.template
import pkg_resources
from onlinejudge_template.types import *


def run(input_format: FormatNode, *, template_file: str) -> bytes:
    data = {
        'input': input_format,
        'config': {},
    }
    directories = [
        str(pathlib.Path(appdirs.user_config_dir('online-judge-tools')) / 'template'),
        pkg_resources.resource_filename('onlinejudge_template_resources', ''),
    ]
    lookup = mako.lookup.TemplateLookup(directories=directories, input_encoding="utf-8", output_encoding="utf-8")
    template = lookup.get_template(template_file)
    return template.render(data=data)