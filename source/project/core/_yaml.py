from typing import Any, IO

import yaml


def dump(data: Any, stream: IO) -> None:
    yaml.dump(data, stream=stream, Dumper=_Dumper, default_flow_style=False)


class _Dumper(yaml.Dumper):

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        # Ignore input indentless to force indentation on lists.
        return super().increase_indent(flow, False)
