"""Independent acceptance checks; keep unchanged during the trial."""
import unittest
from access import can_read


class AccessAcceptance(unittest.TestCase):
    def test_same_tenant_member(self):
        self.assertTrue(can_read({"role": "member", "tenant": "a"}, {"tenant": "a"}))

    def test_other_tenant(self):
        self.assertFalse(can_read({"role": "member", "tenant": "b"}, {"tenant": "a"}))

    def test_guest(self):
        self.assertFalse(can_read({"role": "guest", "tenant": "a"}, {"tenant": "a"}))

    def test_missing_identity(self):
        self.assertFalse(can_read({"role": "member"}, {}))


if __name__ == "__main__":
    unittest.main()
