#!/usr/bin/env python3
"""Check documentation/source contracts without running Teploy or shell examples.

Optionally export shell-tokenized examples for the real Cobra admission test.
This is static evidence, not a deployment/backup/restore acceptance test.
"""
import argparse
import json
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def examples(root):
    """Read indented Teploy examples, joining only explicit continuations."""
    for path in sorted(root.glob('*/README.md')) + [root / 'docs/BACKUPS.md']:
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            if not re.match(r'^\s{4,}teploy\s', line):
                continue
            text = line.strip()
            j = i
            while text.endswith('\\'):
                j += 1
                if j >= len(lines):
                    raise AssertionError(f'{path}:{i+1}: incomplete continuation')
                text = text[:-1].rstrip() + ' ' + lines[j].strip()
            # Never execute command substitution or a displayed placeholder.
            text = re.sub(r'\$\(openssl rand -hex 16\)', 'audit-dummy-password', text)
            values = {'name': 'audit-server', 'app': 'audit-app',
                      'bucket': 'audit-backups', 'region': 'us-east-1',
                      'choose-one': 'audit-dummy-password'}
            text = re.sub(r'<([^>]+)>', lambda m: values[m[1]], text)
            assert '$(' not in text, f'unhandled command substitution in {path}:{i+1}'
            yield {'source': f'{path.relative_to(root)}:{i+1}',
                   'args': shlex.split(text)[1:]}


def flag(args, name):
    before = args[:args.index('--')] if '--' in args else args
    for i, arg in enumerate(before):
        if arg == name:
            return before[i + 1] if i + 1 < len(before) else None
        if arg.startswith(name + '='):
            return arg.split('=', 1)[1]
    return None


def validate(root):
    cases = list(examples(root))
    installs = set()
    for case in cases:
        a = case['args']
        if a[:2] == ['template', 'install']:
            name = a[2]
            manifest = (root / name / 'teploy.yml').read_text()
            host = bool(re.search(r'^ingress:\s*host\s*$', manifest, re.M))
            case['ingress'] = 'host' if host else ''
            assert flag(a, '--server'), case
            assert host or flag(a, '--domain'), case
            assert not any(x.startswith('domain=') for x in a), case
            installs.add(name)
        elif a[:2] == ['app', 'exec']:
            assert flag(a, '--app') and flag(a, '--host') and '--' in a, case
            assert a.index('--') > a.index('--app'), case
            assert a[a.index('--') + 1:], case
        elif a[:1] == ['exec']:
            assert len(a) >= 4 and a[1] == 'audit-server' and a[2] == '--', case
        elif a[:1] in (['restart'], ['logs']):
            assert flag(a, '--app') and flag(a, '--host'), case
        elif a[:2] in (['accessory', 'backup'], ['accessory', 'verify-backup']):
            assert len(a) > 2 and not a[2].startswith('-'), case
            assert '--accessory' not in a, case
            assert flag(a, '--bucket') and flag(a, '--region'), case
            if '--local' in a:
                assert flag(a, '--app'), case
        elif a[:2] == ['backup', 'create']:
            assert flag(a, '--bucket') and flag(a, '--region'), case
        else:
            raise AssertionError(f'Unreviewed command example: {case}')
    expected = {p.parent.name for p in root.glob('*/README.md')}
    assert installs == expected, (installs, expected)
    assert len(installs) == 18, 'Update the expected README coverage when catalog docs change'
    all_readmes = '\n'.join(p.read_text() for p in root.glob('*/README.md'))
    assert '--var domain=' not in all_readmes
    assert 'teploy app restart' not in all_readmes
    assert 'docker exec ollama ' not in all_readmes
    assert ':ollama-cuda' not in (root / 'open-webui/README.md').read_text()
    ship = (root / 'teploy-ship/teploy.yml').read_text()
    assert "app's private" not in ship and 'ufw allow from' not in ship
    for name in ('ollama', 'teploy-ship'):
        doc = (root / name / 'README.md').read_text()
        assert '0.0.0.0' in doc and 'UFW' in doc and 'shared' in doc
    for name in ('ollama', 'open-webui'):
        assert "does not pass Docker's `--gpus`" in (root / name / 'README.md').read_text()
    backup = (root / 'docs/BACKUPS.md').read_text()
    assert 'backup --accessory' not in backup
    assert 'BACKUP ONLY: never run deploy/apply' in backup
    assert 'does **not** save' in backup and 'Do not\n  re-render' in backup
    assert 'TPL-01 remains open' in backup
    assert 'nucleus (generic volume archive, not pg_dump)' in backup
    ha = (root / 'home-assistant/README.md').read_text()
    assert '2026.8 and newer' in ha and 'Older releases using YAML' in ha
    assert 'within five minutes' in ha
    assert 'do not append' in ha and 'REPLACE_WITH_ACTUAL_PROXY_IP' in ha
    manifest = re.search(r'```yaml\n(.*?)\n\s*```', backup, re.S)[1]
    manifest = '\n'.join(line[3:] if line.startswith('   ') else line
                         for line in manifest.splitlines()) + '\n'
    return {'cases': cases, 'backup_manifest': manifest}


def check_source(cli):
    def read(path):
        return (cli / 'internal' / path).read_text()

    def body(path, name):
        source = read(path)
        m = re.search(r'^func ' + re.escape(name) + r'\(', source, re.M)
        assert m, f'missing source function {name}'
        return source[m.start():].split('\nfunc ', 1)[0]

    backup = body('cli/accessory.go', 'newAccessoryBackupCmd')
    assert '"backup <name>"' in backup and 'cobra.ExactArgs(1)' in backup
    assert '"accessory"' not in backup
    for name in ('bucket', 'region', 'app', 'local'):
        assert f'"{name}"' in backup
    for path, name in [('cli/backup.go', 'runBackupCreate'),
                       ('cli/accessory.go', 'runAccessoryBackup')]:
        assert '--bucket is required' in body(path, name)
    assert 'config.LoadApp(".")' in body('cli/backup.go', 'runBackupCreate')
    acc = body('cli/accessory.go', 'runAccessoryBackup')
    assert 'if !local {' in acc and 'loadAppCfgForAccessory()' in acc
    assert 'InspectAccessory(ctx, app, name)' in acc
    assert '--local requires --app' in acc
    assert 'serverName == ""' in body('cli/connect.go', 'connectForApp')
    assert '--host is required when using --app' in body('cli/connect.go', 'resolveApp')
    assert 'cobra.MinimumNArgs(2)' in body('cli/exec.go', 'newExecCmd')
    assert 'strings.Join(args[1:], " ")' in body('cli/exec.go', 'runExec')
    app = body('cli/app.go', 'newAppExecCmd')
    assert '"app"' in app and 'cobra.MinimumNArgs(1)' in app
    assert 'strings.Join(args, " ")' in body('cli/app.go', 'runAppExec')
    assert '"restart"' in body('cli/lifecycle.go', 'newRestartCmd')
    assert 'newAppRestartCmd' not in read('cli/app.go')
    assert 'else if domain == ""' in body('cli/template.go', 'applyTemplateOverrides')
    install = body('cli/template.go', 'runTemplateInstall')
    assert 'os.WriteFile' not in install
    for path in ('docker/docker.go', 'accessories/accessories.go'):
        assert '"--network", "teploy"' in read(path)
    assert '--gpus' not in read('docker/docker.go')
    assert 'yaml:"gpus' not in read('config/app.go')
    assert 'default 0.0.0.0' in read('config/app.go')
    engine = read('backup/backup.go')
    assert 'case isDBType(image, "postgres"):' in engine
    assert 'isDBType(image, "nucleus")' not in engine
    assert 'isDBType(image, "valkey")' not in engine
    assert 'aws CLI not found on server' in engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli-dir', type=Path)
    parser.add_argument('--fixtures', type=Path)
    args = parser.parse_args()
    fixtures = validate(ROOT)
    if args.cli_dir:
        check_source(args.cli_dir)
    if args.fixtures:
        args.fixtures.write_text(json.dumps(fixtures, indent=2) + '\n')
    print(f'docs ok: 18 README install examples; {len(fixtures["cases"])} total commands'
          + ('; CLI source contracts checked' if args.cli_dir else ''))


if __name__ == '__main__':
    main()
