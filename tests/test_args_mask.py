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

class TestKmod(unittest.XXXXXXXX):

    def setUp(self):
        pass


    def test_parse_args(self):

        m1 = "/$app/$app_version/"
        self.k = Kmod(m1)


        t1 = "module load vasp/5.3.5/"

        result = self.k.parse_args(t1)

        self.assertItemsEqual(result, {'$app': 'vasp',
                                    '$version': '5.3.5',
                                    }


    def test_parse_args_t1_short_input(self):



        m1 = "/$app/$app_version/$mpi-$mpi_version-$mpi_compiler-$mpi_compiler_version"



        self.k = Kmod(m1)

        t1 = "module load vasp"

        result = self.k.parse_args(t1)

        self.assertItemsEqual(result, {'$app': 'vasp'}




    def test_parse_args_t1_short_input(self):
        t1 = "module load vasp/5.3.5/mpich-1.8.6-intel-2015"

        result = self.k.parse_args(m1)

        self.assertItemsEqual(result, {'$app': 'vasp',
                                    '$version': '5.3.5',
                                    '$mpi': 'mpich',
                                    '$mpi_version': '1.8.6',
                                    '$mpicompiler': 'intel'
                                    '$mpi_compiler_version': '2015'}




