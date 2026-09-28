"""Regression tests for the CLI's HTTP behaviour."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from tempfile import TemporaryDirectory
from unittest.mock import patch

from click.testing import CliRunner

import pyweek


class DownloadTests(unittest.TestCase):
    def test_download_identifies_itself_to_the_site(self):
        class Handler(BaseHTTPRequestHandler):
            user_agent = None

            def do_GET(self):
                Handler.user_agent = self.headers.get('User-Agent')
                if self.path != '/42/downloads.json':
                    self.send_error(404)
                elif self.headers.get('User-Agent', '').startswith('python-requests/'):
                    self.send_error(403)
                else:
                    body = json.dumps({}).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        with HTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                with TemporaryDirectory() as directory, patch.dict(
                    'os.environ', {'PYWEEK_SKIP_VERSION_CHECK': '1'}
                ), patch.object(
                    pyweek, 'PYWEEK_URL', f'http://127.0.0.1:{server.server_port}'
                ):
                    result = CliRunner().invoke(
                        pyweek.cli, ['download', '--directory', directory, '42']
                    )
                self.assertIsNone(result.exception, result.output)
                self.assertIn('All files downloaded successfully.', result.output)
                self.assertEqual(
                    Handler.user_agent,
                    f'pyweek-cli/{pyweek.__version__} (+https://github.com/pyweekorg/cli)',
                )
            finally:
                server.shutdown()
                thread.join()


if __name__ == '__main__':
    unittest.main()
