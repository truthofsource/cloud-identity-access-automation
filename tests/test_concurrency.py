import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from lab.domain import Directory


class ConcurrencyTests(unittest.TestCase):
    def test_duplicate_workers_commit_one_operation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "journal.db")
            setup = Directory(path)
            setup.db.close()

            def worker(_):
                adapter = Directory(path)
                try:
                    return adapter.apply(
                        "same-request", "join", "employee-001", ["Viewer"], ["Admin"]
                    )
                finally:
                    adapter.db.close()

            with ThreadPoolExecutor(max_workers=4) as workers:
                results = list(workers.map(worker, range(4)))
            self.assertTrue(all(result == results[0] for result in results))
            check = Directory(path)
            try:
                self.assertEqual(
                    check.db.execute("select count(*) from operations").fetchone()[0], 1
                )
                self.assertEqual(
                    check.db.execute("select revision from accounts").fetchone()[0], 1
                )
            finally:
                check.db.close()
