"""Misc os module tests

Made for Jython.
"""
import os
import array
import unittest
from test import test_support

class OSFileTestCase(unittest.TestCase):

    def setUp(self):
        open(test_support.TESTFN, 'w').close()

    def tearDown(self):
        if os.path.exists(test_support.TESTFN):
            os.remove(test_support.TESTFN)

    def test_issue1727(self):
        os.stat(*(test_support.TESTFN,))

    def test_issue1755(self):
        os.remove(test_support.TESTFN)
        self.assertRaises(OSError, os.utime, test_support.TESTFN, None)

    @unittest.skipUnless(hasattr(os, 'link'), "os.link not available")
    def test_issue1824(self):
        os.remove(test_support.TESTFN)
        self.assertRaises(OSError, os.link,
                          test_support.TESTFN, test_support.TESTFN)

    def test_issue1825(self):
        os.remove(test_support.TESTFN)
        testfnu = unicode(test_support.TESTFN)
        try:
            os.open(testfnu, os.O_RDONLY)
        except OSError, e:
            self.assertTrue(isinstance(e.filename, unicode))
            self.assertEqual(e.filename, testfnu)
        else:
            self.assertTrue(False)

        # XXX: currently fail
        #for fn in os.chdir, os.listdir, os.rmdir:
        for fn in (os.rmdir,):
            try:
                fn(testfnu)
            except OSError, e:
                self.assertTrue(isinstance(e.filename, unicode))
                self.assertEqual(e.filename, testfnu)
            else:
                self.assertTrue(False)


class OSDirTestCase(unittest.TestCase):

    def setUp(self):
        self.base = test_support.TESTFN
        self.path = os.path.join(self.base, 'dir1', 'dir2', 'dir3')
        os.makedirs(self.path)

    def test_rmdir(self):
        # Remove end directory
        os.rmdir(self.path)
        # Fail to remove a chain of directories
        self.assertRaises(OSError, os.rmdir, self.base)

    def test_issue2083(self):
        # Should fail to remove/unlink directory
        self.assertRaises(OSError, os.remove, self.path)
        self.assertRaises(OSError, os.unlink, self.path)

    def tearDown(self):
        # Some dirs may have been deleted. Find the longest that exists.
        p = self.path
        while not os.path.exists(p) and p != self.base:
            p = os.path.dirname(p)
        os.removedirs(p)


class OSStatTestCase(unittest.TestCase):

    def setUp(self):
        open(test_support.TESTFN, 'w').close()

    def tearDown(self):
        if os.path.exists(test_support.TESTFN):
            os.remove(test_support.TESTFN)

    def test_stat_with_trailing_slash(self):
        self.assertRaises(OSError, os.stat, test_support.TESTFN + os.path.sep)
        self.assertRaises(OSError, os.lstat, test_support.TESTFN + os.path.sep)


class OSWriteTestCase(unittest.TestCase):

    def setUp(self):
        self.fd = os.open(test_support.TESTFN, os.O_WRONLY | os.O_CREAT)

    def tearDown(self):
        if self.fd :
            os.close(self.fd)
            if os.path.exists(test_support.TESTFN):
                os.remove(test_support.TESTFN)

    def do_write(self, b, nx=None):
        if nx is None : nx = len(b)
        n = os.write(self.fd, b)
        self.assertEqual(n, nx, "os.write length error: " + repr(b))

    def test_write_buffer(self): # Issue 2062
        s = b"Big Red Book"
        for type2test in (str, buffer, bytearray, (lambda x : array.array('b',x))) :
            self.do_write(type2test(s))

        with memoryview(s) as m :
            self.do_write(m)
            # not contiguous:
            self.assertRaises(BufferError, self.do_write, m[1::2])

        # lacks buffer api:
        self.assertRaises(TypeError, self.do_write, 1.5, 4)


def test_main():
    test_support.run_unittest(
        OSFileTestCase, 
        OSDirTestCase,
        OSStatTestCase,
        OSWriteTestCase,
    )

if __name__ == '__main__':
    test_main()
