from splayout.utils import *
import numpy as np
import os
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

class TopologyOptRegion2D:
    """
    2D Optimization region for topology optimization method.

    Parameters
    ----------
    bottom_left_corner_point : Point
        Lower left corner of the region.
    top_right_corner_point : Point
        Upper right corner of the region.
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    x_mesh : Float
        The grid unit in x-axis (unit: μm, default: 0.02).
    y_mesh : Float
        The grid unit in y-axis (unit: μm, default: 0.02).
    z_mesh : Float
        The grid unit in z-axis (unit: μm, default: 0.0071).
    lower_index : Float
        Lower boundary for refractive index (default: 1.444).
    higher_index : Float
        Higher boundary for refractive index (default: 3.478).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: -0.11).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: 0.11).
    rename : String
        New name for the components in Lumerical.
    filter_R : Float
        The radius of smoothing filter (unit: μm, default: 0.5)
    eta : Float
        Eta for the smoothing filter (default: 0.5)
    beta : Float
        Beta fort hte smoothing filter (default: 1)
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, fdtd_engine, x_mesh = 0.02,y_mesh = 0.02,z_mesh = 0.0071, lower_index = 1.444, higher_index = 3.478, z_start=-0.11, z_end=0.11, rename = "ToOptRegion",
                 filter_R = 0.5, eta=0.5, beta=1 ):
        self.left_down_point = tuple_to_point(bottom_left_corner_point)
        self.right_up_point = tuple_to_point(top_right_corner_point)
        self.__last_params = None
        self.__lastest_params = None
        self.fdtd_engine = fdtd_engine
        self.x_mesh = x_mesh
        self.y_mesh = y_mesh
        self.z_mesh = z_mesh
        self.x_min = self.left_down_point.x
        self.x_max = self.right_up_point.x
        self.y_min = self.left_down_point.y
        self.y_max = self.right_up_point.y
        self.z_min = z_start
        self.z_max = z_end
        self.x_size = int((self.x_max - self.x_min)/self.x_mesh) + 1
        self.y_size = int((self.y_max - self.y_min)/self.y_mesh) + 1
        self.z_size = int((self.z_max - self.z_min)/self.z_mesh) + 1
        self.x_positions = np.linspace(self.x_min, self.x_max, self.x_size)
        self.y_positions = np.linspace(self.y_min, self.y_max, self.y_size)
        self.z_positions = np.linspace(self.z_min, self.z_max, self.z_size)
        self.lower_epsilon = lower_index**2
        self.higher_epsilon = higher_index**2
        self.z_start = z_start
        self.z_end = z_end
        self.rename = rename
        self.filter_R = filter_R
        self.eta = eta
        self.beta = beta
        self.index_region_name = self.rename + "_index"
        self.field_region_name = self.rename + "_field"
        self.__initialize()
        self.epsilon_figure = None
        self.field_figure = None

    def __initialize(self):
        self.fdtd_engine.add_index_region(self.left_down_point, self.right_up_point, z_min=self.z_min, z_max=self.z_max, dimension=2, index_monitor_name= self.index_region_name)
        self.fdtd_engine.fdtd.eval( 'select("{}");set("spatial interpolation","specified position");'.format(self.index_region_name))
        self.fdtd_engine.add_field_region(self.left_down_point, self.right_up_point, z_min=self.z_min, z_max=self.z_max, dimension=2, field_monitor_name= self.field_region_name)
        self.fdtd_engine.fdtd.eval(
            'select("{}");set("spatial interpolation","specified position");'.format(self.field_region_name))
        self.fdtd_engine.add_mesh_region(self.left_down_point, self.right_up_point, x_mesh=self.x_mesh, y_mesh=self.y_mesh,
                             z_mesh=self.z_mesh, z_min=self.z_min, z_max=self.z_max)
        self.fdtd_engine.fdtd.eval('addimport;')
        self.fdtd_engine.fdtd.eval('set("detail",1);')
        self.fdtd_engine.fdtd.eval('set("name","{}");'.format(self.rename))

    def get_x_size(self):
        """
        Return x-axis size of the region.

        Returns
        -------
        self.x_size : Int
            x-axis size.
        """
        return self.x_size

    def get_y_size(self):
        """
        Return y-axis size of the region.

        Returns
        -------
        self.y_size : Int
            y-axis size.
        """
        return self.y_size


    def update(self, params_matrix):
        '''
        Update Toopology Optimization Region according to the new matrix.
        (Reference: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        params_matrix : numpy.array
            A two-dimensional array in [0,1].
        '''
        self.fdtd_engine.fdtd.putv("topo_rho", params_matrix)
        self.fdtd_engine.fdtd.eval(('params = struct;'
                       'params.eps_levels=[{0},{1}];'
                       'params.filter_radius = {2};'
                       'params.beta = {3};'
                       'params.eta = {4};'
                       'params.dx = {5};'
                       'params.dy = {6};'
                       'params.dz = 0.0;'
                       'eps_geo = topoparamstoindex(params,topo_rho);').format(self.lower_epsilon, self.higher_epsilon,
                                                                               self.filter_R*1e-6, self.beta, self.eta,
                                                                               self.x_mesh*1e-6, self.y_mesh*1e-6))
        self.fdtd_engine.fdtd.putv('x_geo', self.x_positions*1e-6)
        self.fdtd_engine.fdtd.putv('y_geo', self.y_positions*1e-6)
        self.fdtd_engine.fdtd.putv('z_geo', np.array([self.z_min*1e-6, self.z_max*1e-6]))

        self.fdtd_engine.fdtd.eval('select("{}");'.format(self.rename) +
                  'delete;' +
                  'addimport;' +
                  'set("name","{}");'.format(self.rename) +
                  'temp=zeros(length(x_geo),length(y_geo),2);' +
                  'temp(:,:,1)=eps_geo;' +
                  'temp(:,:,2)=eps_geo;' +
                  'importnk2(sqrt(temp),x_geo,y_geo,z_geo);')

    def get_E_distribution(self, if_get_spatial = 0):
        """
        Get electric field distribution from the region.

        Parameters
        ----------
        if_get_spatial : Bool
            Whether get spatial information as return (default: 0).

        Returns
        -------
        out : Array
            if if_get_spatial == 0: field
                size: (x mesh, y mesh, 1, frequency points, 3).
            if if_get_spatial == 1: field, x mesh, y mesh, z mesh
                size: (x mesh, y mesh, 1, frequency points, 3), (x mesh,), (y mesh,), (1,)
        """
        if (if_get_spatial == 0):
            self.field_figure = self.fdtd_engine.get_E_distribution(field_monitor_name=self.field_region_name,
                                                                    if_get_spatial=if_get_spatial)
            return self.field_figure
        else:
            return self.fdtd_engine.get_E_distribution(field_monitor_name=self.field_region_name,
                                                       if_get_spatial=if_get_spatial)

    def get_epsilon_distribution(self):
        """
        Get epsilon distribution from the region.

        Returns
        -------
        out : Array
            Spectrum, size: (x mesh, y mesh, z mesh, 1).
        """
        return self.fdtd_engine.get_epsilon_distribution(index_monitor_name=self.index_region_name)

    def plot_epsilon_figure(self, filename = None, display = 0):
        """
        Plot epsilon distribution as a heatmap and save it as a file if filename is specified.

        Parameters
        ----------
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).
        display : Int or Bool
            Whether to show the figure (default: 0).

        """
        epsilon = np.real(np.mean(self.epsilon_figure[:,:,0,:] if type(self.epsilon_figure)!=type(None) else self.get_epsilon_distribution()[:,:,0,:], axis=-1))
        xx, yy = np.meshgrid(np.linspace(self.x_positions[0], self.x_positions[-1], epsilon.shape[0]),
                                         np.linspace(self.y_positions[0], self.y_positions[-1], epsilon.shape[1]))
        bar = plt.pcolormesh(xx, yy, epsilon.T , cmap="gray", vmin=self.lower_epsilon, vmax=self.higher_epsilon)
        plt.colorbar(bar)
        plt.xlabel('x (μm)')
        plt.ylabel('y (μm)')
        if (type(filename) != type(None)):
            if (filename[0:2] == './'):
                filepath = os.path.abspath('./') + '/' + filename[2:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            elif (filename[0:3] == '../'):
                filepath = os.path.abspath('../') + '/' + filename[3:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            else:
                plt.savefig(filename)
        if (display):
            plt.show()
        plt.close()



    def plot_field_figure(self, filename = None, display = 0):
        """
        Plot electric distribution as a heatmap and save it as a file if filename is specified.

        Parameters
        ----------
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).
        display : Int or Bool
            Whether to show the figure (default: 0).

        """
        field = np.abs(np.mean(self.field_figure[:, :, 0, 0, :], axis=-1) if type(self.epsilon_figure) != type(
            None) else np.mean(self.get_E_distribution()[:, :, 0, 0, :], axis=-1))
        xx, yy = np.meshgrid(np.linspace(self.x_positions[0], self.x_positions[-1], field.shape[0]),
                             np.linspace(self.y_positions[0], self.y_positions[-1], field.shape[1]))
        bar = plt.pcolormesh(xx, yy, field.T, cmap="jet")
        plt.colorbar(bar)
        plt.xlabel('x (μm)')
        plt.ylabel('y (μm)')
        if (type(filename) != type(None)):
            if (filename[0:2] == './'):
                filepath = os.path.abspath('./') + '/' + filename[2:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            elif (filename[0:3] == '../'):
                filepath = os.path.abspath('../') + '/' + filename[3:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            else:
                plt.savefig(filename)
        if (display):
            plt.show()
        plt.close()