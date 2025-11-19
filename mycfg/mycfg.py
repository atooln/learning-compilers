import json
import sys
from ast import Or
from collections import OrderedDict
from typing import Any, Union

import graphviz

TERMINATORS = ["jmp", "br", "ret"]


def blockify(body):
    block = []

    for inst in body:
        if "op" in inst:
            block.append(inst)

            if inst["op"] in TERMINATORS:
                yield block
                block = []
        else:
            if block:
                yield block
            block = [inst]
    if block:
        yield block


def block_mapper(blocks):
    res = {}
    name = ""
    for b in blocks:
        if "label" in b[0]:
            name = b[0]["label"]
            b = b[1:]
        else:
            name = f"b{len(res)}"

        res[name] = b

    return res


def get_cfg(n2b):
    """
    Given a name to block map:
    produce a mapping from block names -> successor block names
    """
    res = OrderedDict()
    succ = ""
    for i, (name, block) in enumerate(n2b.items()):
        last = block[-1]
        if last["op"] in ("jmp", "br"):
            succ = last["labels"]
        elif last["op"] == "ret":
            succ = ""
        else:
            if i == len(n2b.keys()) - 1:
                succ = []
            else:
                succ = [list(n2b.keys())[i + 1]]

        res[name] = succ

    return res


def mycfg(prog: dict[str, Any]) -> dict[str, str]:
    for f in prog["functions"]:
        n2block = block_mapper(blockify(f["instrs"]))
        cfg = get_cfg(n2block)

        # CFG graphviz
        print(f"digraph {f['name']} {{")  # Added opening brace '{'
        for name in n2block:
            print(f'    "{name}" [shape=box];')

        for name, succs in cfg.items():
            for succ in succs:
                print(f'    "{name}" -> "{succ}";')

        print("}")  # Added the missing closing brace '}'
        # Removed the unnecessary print("")

    return {}


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    mycfg(prog)
