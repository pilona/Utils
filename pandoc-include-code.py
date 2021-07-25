#! /usr/bin/env python3

from pathlib import Path
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
            (_, classes, meta, *_), code = tree.get(
                'c', [[None, None, None], '']
            )
            if code.strip():
                exit('Code in block: ' + '\n'.join(code))
            our_keys = ('include', 'startLine', 'endLine', 'dedent', 'snippet')
            our_options = [(k, v) for k, v in meta if k in our_keys]
            their_options = [(k, v) for k, v in meta if k not in our_keys]

            # TODO: our_classes: .includeLink

            includes = [v for k, v in our_options if k == 'include']
            startlines = [int(v) for k, v in our_options if k == 'startLine']
            endlines = [int(v) for k, v in our_options if k == 'endLine']
            dedents = [int(v) for k, v in our_options if k == 'dedent']
            snippets = [v for k, v in our_options if k == 'snippet']

            if any(our_options) and not includes:
                exit('No file to include', meta)

            if len(includes) > 1:
                exit('More than one include ' + repr(includes))
            if len(startlines) > 1:
                exit('More than one startLine ' + repr(startlines))
            if len(endlines) > 1:
                exit('More than one endLine ' + repr(endlines))
            if len(snippets) > 1:
                exit('More than one snippet ' + repr(snippets))

            if (startlines or endlines) and snippets:
                exit('Cannot have both startLine/endLine and snippet',
                     *startlines, *endlines, *snippets)

            p = Path(includes[0])
            code = p.read_text()
            if startlines or endlines or snippets:
                lines = code.splitlines()

                if snippets:
                    for i, line in enumerate(lines):
                        if line.rstrip() \
                               .endswith('start snippet ' + snippets[0]):
                            startlines = [i + 2]
                        if line.rstrip() \
                               .endswith('end snippet ' + snippets[0]):
                            endlines = [i]
                            break
                    if not startlines:
                        exit('Missing start snippet ' + snippets[0])
                    if not endlines:
                        exit('Missing end snippet ' + snippets[0])

                if endlines:
                    lines = lines[:endlines[0]]
                if startlines:
                    if 'numberLines' in classes:
                        their_options.append([
                            'startFrom',
                            str(startlines[0])
                        ])
                    lines = lines[startlines[0] - 1:]
                code = '\n'.join(lines)

            # Remove up to ```{dedent=dedents[0]}
            #              ```
            # leading spaces of each line. Some lines may remove more than
            # others; that's your problem.
            if dedents:
                code = '\n'.join(
                    next((line.removeprefix(' ' * i)
                          for i
                          in reversed(range(1, dedents[0] + 1))
                          if line.startswith(' ' * i)),
                         line)
                    for line
                    in code.splitlines()
                )
            return {
                't': 'CodeBlock',
                'c': [
                    [
                        '',
                        classes,
                        their_options,
                    ],
                    code
                ],
            }
            # TODO: https://github.com/owickstrom/pandoc-include-code#adding-base-url-for-all-codeblock-links  # noqa

        return tree


if __name__ == '__main__':
    from argparse import ArgumentParser
    from sys import stdin
    argument_parser = ArgumentParser()
    # Don't care about this arg.
    argument_parser.add_argument('outtype')
    args = argument_parser.parse_args()

    ast = json.load(stdin)
    if ast['pandoc-api-version'] != [1, 22]:
        print('Unsupported Pandoc API version',
              '.'.join(map(str, ast['pandoc-api-version'])) + '.',
              'Use at own risk.',
              file=stderr)
    with stdout:
        ast['blocks'] = walktransform(ast['blocks'])
        json.dump(ast, stdout)
    exit()


from contextlib import contextmanager  # noqa
from tempfile import NamedTemporaryFile  # noqa
from textwrap import dedent  # noqa
import subprocess  # noqa


# So I needn't conditionally import pytest.fixture.
@contextmanager
def hello_world():
    with NamedTemporaryFile('w') as f:
        f.write(dedent(r'''
        1
        2
        3
        4
        5
        -- start snippet hello-world
             main =
               putStrLn "Hello world."
        -- end snippet hello-world
        ''').strip())
        f.flush()
        yield f


def test_integration():
    with hello_world() as f:
        assert subprocess.check_output([
            'pandoc',
            '--filter', 'pandoc-include-code.py',
        ], universal_newlines=True, stderr=subprocess.PIPE, input=dedent(rf'''
            `snippet=hello-world`

            ```{{include={f.name} snippet=hello-world dedent=1 .numberLines}}
            ```

            `startLine=7 endLine=8`

            ```{{include={f.name} startLine=7 endLine=8 dedent=1 .numberLines}}
            ```
        ''')).strip() == dedent(r'''
            <p><code>snippet=hello-world</code></p>
            <div class="sourceCode" id="cb1" data-startFrom="7"><pre class="sourceCode numberSource numberLines"><code class="sourceCode" style="counter-reset: source-line 6;"><span id="cb1-7"><a href="#cb1-7"></a>    main =</span>
            <span id="cb1-8"><a href="#cb1-8"></a>      putStrLn &quot;Hello world.&quot;</span></code></pre></div>
            <p><code>startLine=7 endLine=8</code></p>
            <div class="sourceCode" id="cb2" data-startFrom="7"><pre class="sourceCode numberSource numberLines"><code class="sourceCode" style="counter-reset: source-line 6;"><span id="cb2-7"><a href="#cb2-7"></a>    main =</span>
            <span id="cb2-8"><a href="#cb2-8"></a>      putStrLn &quot;Hello world.&quot;</span></code></pre></div>
        ''').strip()  # noqa


def test_startline():
    with hello_world() as f:
        assert walktransform({
            't': 'CodeBlock',
            'c': [
                [
                    '',
                    ['numberLines'],
                    [['include', f.name],
                     ['startLine', '7'],
                     ['endLine', '8']],
                ],
                ''
            ],
        }) == {
            't': 'CodeBlock',
            'c': [
                [
                    '',
                    ['numberLines'],
                    [['startFrom', '7']],
                ],
                '     main =\n'
                '       putStrLn "Hello world."'
            ]
        }


__all__ = (
    'walktransform',
)
