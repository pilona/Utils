#! /usr/bin/env python3

'''
`lsmod` to Graphviz digraph generator

Modules not a dependency of any other (i.e., the top of the multitree, where
the dependencies are at the bottom), are coloured grey.

Use circo for best rendering effect. Expect the graph to be bigger than a
screen. May use twopi, fdp, or sfdp for a sometimes reasonable more compact
layout. Use dot for a large left-to-right or tall top-down graph with
potentially less edge overlap.

Example:

    ./modtree.py -s | circo -Tpng -o modtree.png
    ./modtree.py -g | dot -Tpng -Grankdir=BT -o modtree.png
'''

import subprocess
from typing import NamedTuple, List, Dict, DefaultDict
from itertools import groupby


class Module(NamedTuple):
    name: str
    dependents: List[str]


def to_treedict(lsmod: subprocess.CompletedProcess) -> Dict[str, Module]:
    modules = DefaultDict(list)
    for (module,
         _size,
         _dependent_count,
         *dependents) in map(str.split,
                             lsmod.stdout.splitlines()[1:]):
        # FIXME
        modules[module] += [modules[dependent_module]
                            for dependent_module
                            in dependents and dependents[0].split(',') or []]
    return modules


# No need to return a dictionary, but in case it could be useful to look up…
def to_adjacencylist(lsmod: subprocess.CompletedProcess) -> Dict[str, Module]:
    return {module:
            Module(name=module,
                   dependents=dependents and dependents[0].split(',') or [])
            for (module,
                 _size,
                 _dependent_count,
                 *dependents)
            in map(str.split,
                   lsmod.stdout.splitlines()[1:])}


if __name__ == '__main__':
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    argument_parser = ArgumentParser(epilog=__doc__,
                                     formatter_class=RawDescriptionHelpFormatter)
    argument_parser.add_argument('-s', '--sort',
                                 action='store_true', default=False,
                                 help='Sort modules by number of dependents')
    argument_parser.add_argument('-g', '--group',
                                 action='store_true', default=False,
                                 help='Group modules by distance from top')

    args = argument_parser.parse_args()

    lsmod = subprocess.run(['lsmod'],
                           check=True,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
    adjacency_list = to_adjacencylist(lsmod).values()
    print('digraph {')
    if args.sort or args.group:
        adjacency_list = sorted(adjacency_list,
                                key=lambda module: len(module.dependents))
    if args.group:
        tree_levels = [list(modules)
                       for _, modules
                       in groupby(adjacency_list,
                                  key=lambda module: len(module.dependents))]
        for tree_level in tree_levels:
            print('{ rank=same')
            for module in tree_level:
                print(module.name)
            print('}')
        for tree_level in tree_levels:
            for module in tree_level:
                for dependent in module.dependents:
                    print(module.name, dependent, sep='->')
    else:
        for module in adjacency_list:
            for dependent in module.dependents:
                print(module.name, dependent, sep='->')
            if not module.dependents:
                print(module.name, '[ style = filled ]')
    print('}')
