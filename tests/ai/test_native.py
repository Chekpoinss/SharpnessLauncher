"""End-to-end tests against the actual shipped executable's MCP mode."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import queue
import threading


@unittest.skipUnless(os.environ.get('SHARPNESS_EXE'), 'Set SHARPNESS_EXE to the built launcher')
class NativeMcpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.instance = self.root / 'instances' / 'fabric'
        self.instance.mkdir(parents=True)
        self.cfg = self.instance / 'instance.cfg'
        self.original = b'[General]\nname=Test\n# preserve comment\nJvmArgs=-Dvalue=100%\nMaxMemAlloc=2048\n[Other]\nvalue=keep\n'
        self.cfg.write_bytes(self.original)

    def exchange(self, requests, write=False):
        command = [os.environ['SHARPNESS_EXE'], '--mcp', '--data-dir', str(self.root)]
        if write:
            command.append('--allow-write')
        process = subprocess.run(command, input='\n'.join(requests) + '\n', capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(process.returncode, 0, process.stderr)
        return [json.loads(line) for line in process.stdout.splitlines()]

    def call(self, name, args=None, write=False):
        request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': name, 'arguments': args or {}}}
        return self.exchange([json.dumps(request)], write)[0]['result']

    def decoded(self, result):
        self.assertFalse(result.get('isError'), result)
        return json.loads(result['content'][0]['text'])

    def test_inventory_and_mods(self):
        (self.instance / 'mmc-pack.json').write_text('{"components":[{"uid":"net.fabricmc.fabric-loader","version":"0.16.0"}]}')
        mods = self.instance / '.minecraft/mods'
        mods.mkdir(parents=True)
        (mods / 'sodium.jar').touch()
        self.assertEqual(self.decoded(self.call('list_instances')), [{'id': 'fabric', 'name': 'Test'}])
        result = self.decoded(self.call('inspect_instance', {'instance': 'fabric'}))
        self.assertEqual(result['components'][0]['uid'], 'net.fabricmc.fabric-loader')
        self.assertEqual(result['mods'], ['sodium.jar'])

    def test_memory_permissions_and_recovery(self):
        args = {'instance': 'fabric', 'minimum_mb': 512, 'maximum_mb': 4096, 'confirm': True}
        self.assertTrue(self.call('set_memory', args)['isError'])
        self.assertTrue(self.call('set_memory', dict(args, confirm=False), write=True)['isError'])
        self.assertEqual(self.cfg.read_bytes(), self.original)
        self.decoded(self.call('set_memory', args, write=True))
        self.assertEqual((self.instance / 'instance.cfg.before-ai').read_bytes(), self.original)
        for text in ['MaxMemAlloc=4096', 'MinMemAlloc=512', 'JvmArgs=-Dvalue=100%', '# preserve comment', '[Other]\nvalue=keep']:
            self.assertIn(text, self.cfg.read_text())
        self.assertTrue(self.call('set_memory', args, write=True)['isError'])

    def test_invalid_arguments_leave_files_unchanged(self):
        for low, high in [(True, 4096), (1024.5, 4096), (4096, 512), (512, 999999)]:
            self.assertTrue(self.call('set_memory', {'instance': 'fabric', 'minimum_mb': low, 'maximum_mb': high, 'confirm': True}, write=True)['isError'])
        for value in ['..', '../fabric', 'C:\\secret', '/tmp', 'missing']:
            self.assertTrue(self.call('inspect_instance', {'instance': value})['isError'])
        self.assertEqual(self.cfg.read_bytes(), self.original)

    def test_redaction_and_log_tail(self):
        logs = self.instance / '.minecraft/logs'
        logs.mkdir(parents=True)
        (logs / 'latest.log').write_text('x' * 100000 + '\naccess_token=secret\nBearer private\nAuthorization: Bearer auth-secret\nuser@example.org')
        text = self.decoded(self.call('read_latest_log', {'instance': 'fabric'}))['untrusted_log']
        self.assertLess(len(text), 66000)
        for secret in ['secret', 'private', 'auth-secret', 'user@example.org']:
            self.assertNotIn(secret, text)

    def test_transport_and_notifications(self):
        requests = ['bad json', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'}),
                    json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}),
                    json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})]
        responses = self.exchange(requests)
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0]['error']['code'], -32700)
        self.assertEqual(responses[1]['result']['protocolVersion'], '2025-06-18')
        self.assertEqual({tool['name'] for tool in responses[2]['result']['tools']},
                         {'list_instances', 'inspect_instance', 'read_latest_log', 'set_memory', 'launch_instance'})

    def test_launch_requires_permissions(self):
        self.assertTrue(self.call('launch_instance', {'instance': 'fabric', 'confirm': True})['isError'])
        self.assertTrue(self.call('launch_instance', {'instance': 'fabric', 'confirm': False}, write=True)['isError'])

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            try:
                (self.root / 'instances' / 'escape').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('Symlink creation is unavailable')
            self.assertTrue(self.call('inspect_instance', {'instance': 'escape'})['isError'])

    def test_persistent_client_receives_reply_before_closing_stdin(self):
        process = subprocess.Popen([os.environ['SHARPNESS_EXE'], '--mcp', '--data-dir', str(self.root)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding='utf-8')
        replies = queue.Queue()
        threading.Thread(target=lambda: replies.put(process.stdout.readline()), daemon=True).start()
        try:
            process.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': 7, 'method': 'ping'}) + '\n')
            process.stdin.flush()
            response = json.loads(replies.get(timeout=10))
            self.assertEqual(response, {'jsonrpc': '2.0', 'id': 7, 'result': {}})
            process.stdin.close()
            process.wait(timeout=10)
            self.assertEqual(process.returncode, 0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()


if __name__ == '__main__':
    unittest.main()
