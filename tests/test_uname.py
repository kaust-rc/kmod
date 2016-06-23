#!/usr/bin/env python

import unittest
import platform


class Uname(self):
    """
    https://docs.python.org/2/library/platform.html
    """
    def __init__(self):
        self.set_uname()

    def set_uanme(self):
        """
        Method to set all uname parameters on the class.  If platform and uname are different
        then add both.  Uname is used/aliased as it will be more familiar to Linux admins.
        """
        pass



class testLoadYaml(unittest.TestCase):

    def setUp(self):
        #You will have to set up a mocked platform here
        pass


    def test_uname(self):
        u = Uname()

        self.assertTrue(u.kernel_version, "GNU/Linux")
        self.assertTrue(u.nodename, "mocked hostname")



