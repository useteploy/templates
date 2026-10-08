"""Mutation checks: known bad documentation must fail the static gate."""
import shutil
import tempfile
import unittest
from pathlib import Path

import validate_docs


class DocumentationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'templates'
        shutil.copytree(validate_docs.ROOT, self.root,
                        ignore=shutil.ignore_patterns('__pycache__'))

    def change(self, path, old, new):
        file = self.root / path
        text = file.read_text()
        self.assertIn(old, text)
        file.write_text(text.replace(old, new))

    def test_current_documentation(self):
        result = validate_docs.validate(self.root)
        self.assertEqual(len(result['cases']), 30)
        self.assertIn('server: my-server', result['backup_manifest'])
        # Shell quoting must preserve a complete remote command as one argument.
        cp = next(c for c in result['cases'] if c['args'][-1].startswith('cp -p '))
        self.assertEqual(cp['args'][-1],
                         'cp -p /config/configuration.yaml /config/configuration.yaml.before-proxy')

    def test_each_domain_flag_regression(self):
        checked = 0
        for path in sorted(self.root.glob('*/README.md')):
            original = path.read_text()
            if '--domain ' not in original:
                continue
            with self.subTest(template=path.parent.name):
                path.write_text(original.replace('--domain ', '--var domain='))
                with self.assertRaises(AssertionError):
                    validate_docs.validate(self.root)
                path.write_text(original)
                checked += 1
        self.assertEqual(checked, 17)

    def test_invalid_accessory_backup_flag(self):
        self.change('docs/BACKUPS.md', 'teploy accessory backup db',
                    'teploy accessory backup --accessory db')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_missing_backup_bucket(self):
        self.change('docs/BACKUPS.md', '--bucket <bucket>', '')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_invalid_home_assistant_restart(self):
        self.change('home-assistant/README.md', 'teploy restart --app homeassistant',
                    'teploy app restart homeassistant')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_missing_app_exec_host(self):
        self.change('home-assistant/README.md', '--host <name>', '')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_wrong_ollama_container(self):
        self.change('ollama/README.md',
                    'teploy app exec --app ollama --host <name> -- ollama pull llama3.2',
                    'teploy exec <name> -- docker exec ollama ollama pull llama3.2')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_unsafe_network_claim(self):
        self.change('teploy-ship/teploy.yml',
                    'a tested upstream/Docker-aware firewall boundary',
                    'ufw allow from 100.64.0.0/10 to any port 7460')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)

    def test_unsupported_gpu_claim(self):
        self.change('open-webui/README.md', 'The template deploys the CPU path',
                    'Change the image to :ollama-cuda. The template deploys the CPU path')
        with self.assertRaises(AssertionError):
            validate_docs.validate(self.root)


if __name__ == '__main__':
    unittest.main()
