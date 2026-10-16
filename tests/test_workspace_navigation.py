"""Close a feature to return home; close home to exit the application."""
import sys
from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from views.workspace import WorkspaceApp


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = WorkspaceApp(self.root)

    def tearDown(self):
        try:
            if self.root.winfo_exists():
                self.app.close()
        except tk.TclError:
            pass

    def close_window(self, window):
        self.root.tk.call(window.protocol('WM_DELETE_WINDOW'))

    def assert_exited(self):
        with self.assertRaises(tk.TclError):
            self.root.winfo_exists()

    def test_post_closes_selector_and_returns_to_new_selector(self):
        first_selector = self.app.selector
        self.app.open_post()
        self.assertFalse(first_selector.winfo_exists())
        self.assertIsNone(self.app.selector)
        post = self.app.post_app
        self.close_window(self.app.post_window)
        self.assertTrue(post.closed)
        self.assertIsNone(self.app.post_app)
        self.assertEqual(self.app.selector.state(), 'normal')
        self.app.open_post()
        self.assertIsNot(self.app.post_app, post)
        self.close_window(self.app.post_window)
        self.close_window(self.app.selector)
        self.assert_exited()

    def test_live_returns_home_and_stops_receiving(self):
        self.app.open_live()
        live = self.app.live_window
        receiver = Mock()
        live.receiver = receiver
        self.close_window(live)
        self.assertTrue(live.closed)
        receiver.stop.assert_called_once()
        self.assertIsNone(self.app.live_window)
        self.assertEqual(self.app.selector.state(), 'normal')
        self.app.open_live()
        self.assertIsNot(self.app.live_window, live)
        self.close_window(self.app.live_window)
        self.close_window(self.app.selector)
        self.assert_exited()

    def test_switch_preserves_session_but_return_home_closes_both(self):
        self.app.open_post()
        post = self.app.post_app
        post.open_live()
        live = self.app.live_window
        self.assertEqual(self.app.post_window.state(), 'withdrawn')
        live.open_post()
        self.assertIs(self.app.post_app, post)
        self.assertEqual(live.state(), 'withdrawn')
        self.assertNotEqual(self.app.post_window.state(), 'withdrawn')
        self.assertIsNone(self.app.selector)
        self.close_window(self.app.post_window)
        self.assertTrue(live.closed)
        self.assertTrue(post.closed)
        self.assertEqual(self.app.selector.state(), 'normal')
        self.close_window(self.app.selector)
        self.assert_exited()

    def test_post_return_cancels_pending_analysis_poll(self):
        self.app.open_post()
        post = self.app.post_app
        post.busy = True
        post.poll_timer = post.root.after(10000, post.poll)
        timer = post.poll_timer
        self.close_window(self.app.post_window)
        self.assertNotIn(timer, self.root.tk.call('after', 'info'))
        self.assertEqual(self.app.selector.state(), 'normal')
        self.close_window(self.app.selector)
        self.assert_exited()


if __name__ == '__main__':
    unittest.main()
