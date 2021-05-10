"""
    Unify project files structure, including:
    - custom docstring block describing file function
    - imports block
    - author block (include version, licence, copyright, maintainer and email as well)
    - code block
"""

import os
import re
import sys


author = '''
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/0.0.0/LICENSE"
__version__ = "0.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"
'''


author_ptn = re.escape(author.strip()).replace("0\.0\.0", "\d\.\d\.\d+")

py_file_struc_ptn = '(?P<service>(?:\#[^\n]+\n+)+){{,1}}\n*' \
                    '(?P<docstr>(?:\'\'\'.+?\'\'\'|""".+?""")){{,1}}\n*' \
                    '(?P<author>{author_ptn}){{,1}}\n*' \
                    '(?P<imports>(?:^(?:#|import|from|\s{{4,}})[^\n]+\n+)+){{,1}}\n*' \
                    '(?P<code>.*)'.format(author_ptn=author_ptn)
py_file_struc_re = re.compile(py_file_struc_ptn, re.M | re.S)

release_version_re = re.compile(r'\d\.\d\.\d+')

parse_paths = ['lexnlp', 'lexnlpprivate']
exclude_paths = []


def unify_file_structure(release_number):
    base_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), '../..'))
    paths = [os.path.join(base_dir, p) for p in parse_paths]

    files = sorted([os.path.join(a, i)
                    for path in paths
                    for a, _, b in os.walk(path)
                    for i in b
                    if i.endswith('.py')])
    if exclude_paths:
        files = files + [os.path.join(base_dir, i) for i in os.listdir(base_dir)
                         if i.endswith('.py') and i not in exclude_paths]

    global author
    author = release_version_re.sub(release_number, author)

    for a_file in files:
        with open(a_file, 'r') as f:
            file_content_str = f.read()

        match = py_file_struc_re.fullmatch(file_content_str)

        if match:
            current_structure = match.groupdict()

            service = (current_structure['service'] or '').strip()
            docstr = (current_structure['docstr'] or '').strip()
            imports = (current_structure['imports'] or '').strip()
            code = (current_structure['code'] or '').strip()
        else:
            service = imports = code = docstr = ''

        new_file_content = ''.join([
            service.strip(),
            '\n'*2 if service else '',
            docstr.strip(),
            '\n'*2 if docstr else '',
            author.strip(),
            '\n'*3 if code else '',
            imports,
            '\n'*3 if imports else '',
            code,
            '\n'
        ])

        # search problems
        if new_file_content.count('__author__') > 1:
            print('>>> WARN!!! Duplicated author block: {a_file}'.format(a_file=a_file))
            # continue

        with open(a_file, 'w') as f:
            f.write(new_file_content)
        print('Done: {a_file}'.format(a_file=a_file))


if __name__ == '__main__':
    release_version = None
    args = sys.argv
    if len(args) == 1:
        print('Provide release number in format "1.2.3"')
        exit(1)
    if len(args) == 2:
        release_version = args[1]
        if not release_version_re.fullmatch(release_version):
            print('Wrong release number format "1.2.3"')
            exit(1)
    unify_file_structure(release_version)
