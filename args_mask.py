
import unittest


class Kmod(object):


    def __init__(self, args_mask):
        """
        This mask will determine from the module load command, how to assign
        variables to each segment

        args_mask will be defined in the yaml file
        example args_mask: /$app/$app_version/
        """
        self.args_mask = args_mask



    def parse_args(args=""):
        """
        Method to take in a string and return a
        dict with k:v of pairs of arguments
        """
        return dict()




#put this in separate file.


#Use nosetests to automate calling

#Make sure pylint is above 8.0 for both test code and dev code

#Good luck

