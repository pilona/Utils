#! /usr/bin/env python3

from sys import stdout, stderr, exit
import json


def walktransform(tree):
    if isinstance(tree, list):
        return [walktransform(subtree)
                for subtree
                in tree]
    elif not isinstance(tree, dict):
        exit('Unsupported AST node', type(tree))
    elif isinstance(tree, dict):
        if tree.get('t') == 'CodeBlock':
            (_, _, meta, *_), code = tree.get('c', [[None, None, None], ''])
            if code.strip():
                breakpoint()
                exit('Code in block:', code, sep='\n')
            includes = [v for k, v in meta if k == 'include']
            if len(includes) > 1:
                exit('Too many includes', *includes)
            elif not includes:
                exit('No file to include', meta)
            else:
                with open(includes[0]) as fp:
                    code = fp.read()
                return {
                    't': 'CodeBlock',
                    'c': [
                        [
                            '',
                            [],
                            [
                                # TODO: file type
                            ],
                        ],
                        code
                    ],
                }

            # TODO: https://github.com/owickstrom/pandoc-include-code#snippets
            # TODO: https://github.com/owickstrom/pandoc-include-code#ranges
            # TODO: https://github.com/owickstrom/pandoc-include-code#dedent
            # TODO: https://github.com/owickstrom/pandoc-include-code#adding-base-url-for-all-codeblock-links  # noqa


if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    argument_parser = ArgumentParser()
    argument_parser.add_argument('ast', type=FileType('r'), default='-')
    args = argument_parser.parse_args()

    ast = json.load(args.ast)
    if ast['pandoc-api-version'] != (1, 22):
        print('Unsupported Pandoc API version',
              '.'.join(map(str, ast['pandoc-api-version'])) + '.',
              'Use at own risk.',
              file=stderr)
    json.dump(walktransform(ast['blocks']), stdout)
