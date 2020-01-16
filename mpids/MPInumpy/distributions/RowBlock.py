from mpi4py import MPI
import numpy as np

from mpids.MPInumpy.MPIArray import MPIArray
from mpids.MPInumpy.errors import ValueError
from mpids.MPInumpy.utils import determine_redistribution_counts_from_shape, \
                                 distribute_shape,                           \
                                 format_indexed_result,                      \
                                 global_to_local_key

from mpids.MPInumpy.mpi_utils import all_gather_v, all_to_all_v
from mpids.MPInumpy.distributions.Undistributed import Undistributed


"""
    RowBlock implementation of MPIArray abstract base class.
"""
class RowBlock(MPIArray):

#TODO: Resolve this namespace requirement
    def __getitem__(self, key):
        local_key = global_to_local_key(key,
                                        self.globalshape,
                                        self.local_to_global)
        indexed_result = self.base.__getitem__(local_key)
        indexed_result = format_indexed_result(key, indexed_result)

        distributed_result =  self.__class__(np.copy(indexed_result),
                                             comm=self.comm,
                                             comm_dims=self.comm_dims,
                                             comm_coord=self.comm_coord)
        #Return undistributed copy of data
        return distributed_result.collect_data()


    #Unique properties to MPIArray
    @property
    def dist(self):
        return 'b'


    @property
    def globalshape(self):
        if self._globalshape is None:
                self.__globalshape()
        return self._globalshape

    def __globalshape(self):
        axis0_len = self.__custom_reduction(MPI.SUM, np.asarray(self.shape[0]))
        comm_shape = [int(axis0_len[0])]
        if len(self.shape) == 2:
                axis_len = self.__custom_reduction(MPI.MAX,
                                                   np.asarray(self.shape[1]))
                comm_shape.append(int(axis_len[0]))

        self._globalshape = tuple(comm_shape)


    @property
    def globalsize(self):
        if self._globalsize is None:
                self.__globalsize()
        return self._globalsize

    def __globalsize(self):
        comm_size = np.empty(1, dtype='int')
        self.comm.Allreduce(np.array(self.size), comm_size, op=MPI.SUM)
        self._globalsize = int(comm_size)


    @property
    def globalnbytes(self):
        if self._globalnbytes is None:
                self.__globalnbytes()
        return self._globalnbytes

    def __globalnbytes(self):
        comm_nbytes = np.empty(1, dtype='int')
        self.comm.Allreduce(np.array(self.nbytes), comm_nbytes, op=MPI.SUM)
        self._globalnbytes = int(comm_nbytes)


    @property
    def globalndim(self):
        if self._globalndim is None:
            self.__globalndim()
        return self._globalndim

    def __globalndim(self):
        self._globalndim = int(len(self.globalshape))


    #Custom reduction method implementations
    def max(self, **kwargs):
        self.check_reduction_parms(**kwargs)
        local_max = np.asarray(self.base.max(**kwargs))
        global_max = self.__custom_reduction(MPI.MAX, local_max, **kwargs)
        return Undistributed(global_max, comm=self.comm)


    def mean(self, **kwargs):
        global_sum = self.sum(**kwargs)
        axis = kwargs.get('axis')
        if axis is not None:
            global_mean = global_sum * 1. / self.globalshape[axis]
        else:
            global_mean = global_sum * 1. / self.globalsize

        return Undistributed(global_mean, comm=self.comm)


    def min(self, **kwargs):
        self.check_reduction_parms(**kwargs)
        local_min = np.asarray(self.base.min(**kwargs))
        global_min = self.__custom_reduction(MPI.MIN, local_min, **kwargs)
        return Undistributed(global_min, comm=self.comm)


    def std(self, **kwargs):
        axis = kwargs.get('axis')
        local_mean = self.mean(**kwargs)

        if axis == 1:
            row_min, row_max = self.local_to_global[0]
            local_mean = local_mean[row_min: row_max]
#TODO: Explore np kwarg 'keepdims' to avoid force transpose
            #Force a transpose
            local_mean = local_mean.reshape(self.shape[0], 1)

        local_square_diff = (self - local_mean)**2
        local_sum_square_diff = np.asarray(local_square_diff.base.sum(**kwargs))
        global_sum_square_diff = \
            self.__custom_reduction(MPI.SUM,
                                    local_sum_square_diff,
                                    dtype=local_sum_square_diff.dtype,
                                    **kwargs)
        if axis is not None:
            global_std = np.sqrt(
                global_sum_square_diff * 1. / self.globalshape[axis])
        else:
            global_std = np.sqrt(global_sum_square_diff * 1. / self.globalsize)

        return Undistributed(global_std, comm=self.comm)


    def sum(self, **kwargs):
        self.check_reduction_parms(**kwargs)
        local_sum = np.asarray(self.base.sum(**kwargs))
        global_sum = self.__custom_reduction(MPI.SUM, local_sum, **kwargs)
        return Undistributed(global_sum, comm=self.comm)


    def __custom_reduction(self, operation, local_red, axis=None, dtype=None,
                         out=None):
        if dtype is None: dtype = local_red.dtype

        if axis is None or axis == 0:
            global_red = np.empty(local_red.size, dtype=dtype)
            self.comm.Allreduce(local_red, global_red, op=operation)
        if axis == 1:
            global_red = all_gather_v(local_red, comm=self.comm)

        return global_red


    def collect_data(self):
        global_data = all_gather_v(self, shape=self.globalshape, comm=self.comm)
        return Undistributed(global_data, comm=self.comm)


    def reshape(self, *args):
        if np.prod(args) != self.globalsize:
            raise ValueError("cannot reshape global array of size",
                             self.globalsize,"into shape", tuple(args))
#TODO: Clean this nonsense up
        local_shape, comm_dims, comm_coord, local_to_global = \
            distribute_shape(args, self.dist, comm=self.comm)

        send_counts, recv_counts = \
            determine_redistribution_counts_from_shape(self.globalshape,
                                                       args,
                                                       self.dist,
                                                       comm=self.comm)

        local_data = all_to_all_v(self, send_counts, recv_counts,
                                  recv_shape=local_shape, comm=self.comm)

        return self.__class__(np.copy(local_data),
                              comm=self.comm,
                              comm_dims=comm_dims,
                              comm_coord=comm_coord,
                              local_to_global=local_to_global)
