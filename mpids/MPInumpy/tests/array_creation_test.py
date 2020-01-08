import unittest
import numpy as np
from mpi4py import MPI
import mpids.MPInumpy as mpi_np
from mpids.MPInumpy.distributions import *
from mpids.MPInumpy.errors import InvalidDistributionError

class ArrayCreationErrorsPropegatedTest(unittest.TestCase):

    def test_unsupported_distribution(self):
        data = np.array(list(range(10)))
        comm = MPI.COMM_WORLD
        with self.assertRaises(InvalidDistributionError):
            mpi_np.array(data, comm=comm, dist='bananas')
        # Test cases where dim input data != dim distribution
        with self.assertRaises(InvalidDistributionError):
            mpi_np.array(data, comm=comm, dist=('*', 'b'))
        with self.assertRaises(InvalidDistributionError):
            mpi_np.array(data, comm=comm, dist=('b','b'))


class ArrayDefaultTest(unittest.TestCase):
    """ MPIArray creation routine.
        See mpids.MPInumpy.tests.MPIArray_test for more exhaustive evaluation
    """

    def create_setUp_parms(self):
        parms = {}
        parms['np_data'] = np.array(list(range(20))).reshape(5,4)
        parms['array_like_data'] = parms['np_data'].tolist()
        parms['comm'] = MPI.COMM_WORLD
        # Default distribution
        parms['dist'] = 'b'
        parms['dist_class'] = RowBlock
        return parms


    def setUp(self):
        parms = self.create_setUp_parms()
        self.np_data = parms['np_data']
        self.array_like_data = parms['array_like_data']
        self.comm = parms['comm']
        self.dist = parms['dist']
        self.dist_class = parms['dist_class']
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def test_return_behavior_with_np_data_from_all_ranks(self):
        for root in range(self.size):
            np_data = None
            self.assertTrue(np_data is None)
            if self.rank == root:
                np_data = self.np_data
            mpi_np_array = mpi_np.array(np_data,
                                        comm=self.comm,
                                        root=root,
                                        dist=self.dist)
            self.assertTrue(isinstance(mpi_np_array, mpi_np.MPIArray))
            self.assertTrue(isinstance(mpi_np_array, self.dist_class))
            self.assertEqual(mpi_np_array.comm, self.comm)
            self.assertEqual(mpi_np_array.dist, self.dist)


    def test_return_behavior_with_array_like_data_from_all_ranks(self):
        for root in range(self.size):
            array_like_data = None
            self.assertTrue(array_like_data is None)
            if self.rank == root:
                array_like_data = self.array_like_data
            mpi_np_array = mpi_np.array(array_like_data,
                                        comm=self.comm,
                                        root=root,
                                        dist=self.dist)
            self.assertTrue(isinstance(mpi_np_array, mpi_np.MPIArray))
            self.assertTrue(isinstance(mpi_np_array, self.dist_class))
            self.assertEqual(mpi_np_array.comm, self.comm)
            self.assertEqual(mpi_np_array.dist, self.dist)


class ArrayUndistributedTest(ArrayDefaultTest):

    def create_setUp_parms(self):
        parms = {}
        parms['np_data'] = np.array(list(range(20))).reshape(5,4)
        parms['array_like_data'] = parms['np_data'].tolist()
        parms['comm'] = MPI.COMM_WORLD
        # Undistributed distribution
        parms['dist'] = 'u'
        parms['dist_class'] = Undistributed
        return parms


class EmptyDefaultTest(unittest.TestCase):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Default distribution
        parms['dist'] = 'b'
        parms['dist_class'] = RowBlock
        return parms


    def setUp(self):
        parms = self.create_setUp_parms()
        self.shape = parms['shape']
        self.comm = parms['comm']
        self.dist = parms['dist']
        self.dist_class = parms['dist_class']
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def test_return_behavior_from_all_ranks(self):
        for root in range(self.size):
            shape = None
            self.assertTrue(shape is None)
            if self.rank == root:
                shape = self.shape
            mpi_np_empty = mpi_np.empty(shape,
                                        comm=self.comm,
                                        root=root,
                                        dist=self.dist)
            self.assertTrue(isinstance(mpi_np_empty, mpi_np.MPIArray))
            self.assertTrue(isinstance(mpi_np_empty, self.dist_class))
            self.assertEqual(mpi_np_empty.comm, self.comm)
            self.assertEqual(mpi_np_empty.dist, self.dist)


class EmptyUndistributedTest(EmptyDefaultTest):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Undistributed distribution
        parms['dist'] = 'u'
        parms['dist_class'] = Undistributed
        return parms


class OnesDefaultTest(unittest.TestCase):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Default distribution
        parms['dist'] = 'b'
        parms['dist_class'] = RowBlock
        return parms


    def setUp(self):
        parms = self.create_setUp_parms()
        self.shape = parms['shape']
        self.comm = parms['comm']
        self.dist = parms['dist']
        self.dist_class = parms['dist_class']
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def test_return_behavior_from_all_ranks(self):
        for root in range(self.size):
            shape = None
            self.assertTrue(shape is None)
            if self.rank == root:
                shape = self.shape
            mpi_np_ones = mpi_np.ones(shape,
                                      comm=self.comm,
                                      root=root,
                                      dist=self.dist)
            self.assertTrue(isinstance(mpi_np_ones, mpi_np.MPIArray))
            self.assertTrue(isinstance(mpi_np_ones, self.dist_class))
            self.assertEqual(mpi_np_ones.comm, self.comm)
            self.assertEqual(mpi_np_ones.dist, self.dist)
            self.assertTrue(np.alltrue((mpi_np_ones) == (1)))


class OnesUndistributedTest(OnesDefaultTest):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Undistributed distribution
        parms['dist'] = 'u'
        parms['dist_class'] = Undistributed
        return parms


class ZerosDefaultTest(unittest.TestCase):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Default distribution
        parms['dist'] = 'b'
        parms['dist_class'] = RowBlock
        return parms


    def setUp(self):
        parms = self.create_setUp_parms()
        self.shape = parms['shape']
        self.comm = parms['comm']
        self.dist = parms['dist']
        self.dist_class = parms['dist_class']
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def test_return_behavior_from_all_ranks(self):
        for root in range(self.size):
            shape = None
            self.assertTrue(shape is None)
            if self.rank == root:
                shape = self.shape
            mpi_np_zeros = mpi_np.zeros(shape,
                                        comm=self.comm,
                                        root=root,
                                        dist=self.dist)
            self.assertTrue(isinstance(mpi_np_zeros, mpi_np.MPIArray))
            self.assertTrue(isinstance(mpi_np_zeros, self.dist_class))
            self.assertEqual(mpi_np_zeros.comm, self.comm)
            self.assertEqual(mpi_np_zeros.dist, self.dist)
            self.assertTrue(np.alltrue((mpi_np_zeros) == (0)))


class ZerosUndistributedTest(ZerosDefaultTest):

    def create_setUp_parms(self):
        parms = {}
        parms['shape'] = (5, 4)
        parms['comm'] = MPI.COMM_WORLD
        # Undistributed distribution
        parms['dist'] = 'u'
        parms['dist_class'] = Undistributed
        return parms


if __name__ == '__main__':
    unittest.main()
