"""Static, offline documentation claim audit."""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import sys

from . import __version__
from .phrases import VINVALIDATION, NOVINVALIDATION, GENERIC_NAMES

def _targets(node):
    if isinstance(node, ast.Name):
        yield node.id
    elif isinstance(node, (ast.Tuple, ast.List)):
        for element in node.elts:
            yield from _targets(element)


def evidence(source):
    """Inspect one module without executing it."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return False
    imports, bound, definitions, assignments = {}, set(), set(), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                imports[item.asname or item.name.split('.')[0]] = item.name if item.asname else item.name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for item in node.names:
                if item.name != '*':
                    imports[item.asname or item.name] = node.module + '.' + item.name
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                bound.update(_targets(target)); assignments.append((target, node.value))
        elif isinstance(node, ast.AnnAssign):
            bound.update(_targets(node.target)); assignments.append((node.target, node.value))
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars:
                    bound.update(_targets(item.optional_vars)); assignments.append((item.optional_vars, item.context_expr))
    shadowed = bound | definitions
    def resolve(expr):
        parts = []
        while isinstance(expr, ast.Attribute):
            parts.append(expr.attr); expr = expr.value
        if not isinstance(expr, ast.Name) or expr.id not in imports or expr.id in shadowed:
            return None
        return '.'.join([imports[expr.id]] + list(reversed(parts)))
    def is_class(expr, kind):
        return resolve(expr) == kind
    def instance(expr, kind):
        if isinstance(expr, ast.Call):
            return is_class(expr.func, kind)
        if isinstance(expr, ast.Name) and expr.id not in definitions and not (expr.id in imports and expr.id in shadowed):
            return any(isinstance(target, ast.Name) and target.id == expr.id and isinstance(value, ast.Call) and is_class(value.func, kind) for target, value in assignments)
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        resolved = resolve(func)
        name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ''
        if name in definitions:
            continue
        if resolved == 'vininfo.Vin':
            return True
        if resolved == 'vin.VIN':
            if not any(k.arg == 'fix_check_digit' and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
                return True
        if resolved in ('vininfo.Vin.validate', 'pyvin.utils.clean_vins'):
            return True
        if isinstance(func, ast.Attribute):
            base = func.value
            if func.attr in ('validate', 'verify_checksum') and (instance(base, 'vininfo.Vin') or is_class(base, 'vininfo.Vin')):
                return True
            if func.attr == 'calculate_check_digit' and (instance(base, 'vin.VIN') or is_class(base, 'vin.VIN')):
                return True
            if func.attr in GENERIC_NAMES:
                root = base
                while isinstance(root, ast.Attribute):
                    root = root.value
                if not (isinstance(root, ast.Name) and root.id in imports and root.id in shadowed):
                    return True
        if isinstance(func, ast.Name) and resolved and resolved.rsplit('.', 1)[-1] in GENERIC_NAMES and resolved.rsplit('.', 1)[-1] not in definitions:
            return True

    return False


def _normalize(text):
    return ' '.join(text.lower().replace('n\u2019t', ' not').replace("n't", ' not').replace('-', ' ').split())


def _pattern(phrases):
    return re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(p) for p in sorted(phrases, key=lambda p: (-len(p), p))) + r')(?!\w)')

YES = _pattern(VINVALIDATION)
NO = _pattern(NOVINVALIDATION)
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')


def claims(text):
    paragraphs, current, fence = [], [], None
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not line[match.end():].strip():
                fence = None
            continue
        if match:
            if current:
                paragraphs.append(' '.join(current)); current = []
            fence = match.group(1)
        elif not line.strip():
            if current:
                paragraphs.append(' '.join(current)); current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(' '.join(current))
    yes, no = set(), set()
    for paragraph in paragraphs:
        normalized = _normalize(paragraph)
        no.update(m.group() for m in NO.finditer(normalized))
        yes.update(m.group() for m in YES.finditer(NO.sub(' ', normalized)))
    return yes, no


def audit(root, ignore=()):
    root = Path(root)
    if not root.is_dir() or root.is_symlink() or not os.access(root, os.R_OK | os.X_OK):
        raise OSError('root is not a readable directory: {}'.format(root))
    ignores = [str(x).replace('\\', '/').strip('/') for x in ignore]
    yes, no, production, tests = set(), set(), [], []
    def skipped(rel):
        return any(rel == p or rel.startswith(p + '/') for p in ignores if p)
    def walk_error(error):
        raise error
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        dirs[:] = [d for d in dirs if not (base / d).is_symlink() and not skipped((base / d).relative_to(root).as_posix())]
        for name in files:
            path = base / name
            rel = path.relative_to(root)
            if path.is_symlink() or skipped(rel.as_posix()):
                continue
            parts = rel.parts
            if (rel.as_posix() == 'README.md' or ('docs' in parts[:-1] and path.suffix == '.md')):
                a, b = claims(path.read_text(encoding='utf-8'))
                yes.update(a); no.update(b)
            if path.suffix == '.py' and not set(parts[:-1]).intersection(('fixtures', 'docs', 'examples')):
                is_test = 'tests' in parts[:-1] or name.startswith('test_') or name.endswith('_test.py')
                if evidence(path.read_text(encoding='utf-8')):
                    (tests if is_test else production).append(rel.as_posix())
    findings = []
    if yes and not production:
        findings.append({'id': 'documented-vin-validation-claim-false', 'severity': 'MEDIUM' if tests else 'HIGH', 'phrases': sorted(yes), 'evidence': sorted(tests)})
    if no and production:
        findings.append({'id': 'documented-no-vin-validation-claim-false', 'severity': 'HIGH', 'phrases': sorted(no), 'evidence': sorted(production)})
    return findings


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, '{}: error: {}\n'.format(self.prog, message))


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    subs = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    sub = subs.add_parser('audit', help='audit a repository')
    sub.add_argument('repo', nargs='?', default='.')
    sub.add_argument('--json', action='store_true')
    sub.add_argument('--verbose', action='store_true')
    sub.add_argument('--ignore', action='append', default=[], metavar='PREFIX')
    sub.add_argument('--fail-on', choices=('high', 'medium'), default='high')
    args = parser.parse_args(argv)
    try:
        findings = audit(args.repo, args.ignore)
    except (OSError, UnicodeError) as exc:
        print('error: {}'.format(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({'findings': findings}, indent=2))
    elif not findings:
        print('PASS')
    else:
        for finding in findings:
            print('{} {}'.format(finding['severity'], finding['id']))
            if args.verbose:
                print('  phrases: ' + ', '.join(finding['phrases']))
                if finding['evidence']:
                    print('  evidence: ' + ', '.join(finding['evidence']))
    return 2 if any(f['severity'] == 'HIGH' or args.fail_on == 'medium' for f in findings) else 0
