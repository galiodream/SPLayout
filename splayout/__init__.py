__version__ = "0.3.5"

from splayout.AEMDgrating import MAKE_AEMD_GRATING
from splayout.bend import Bend
from splayout.doubleconnector import DoubleBendConnector
from splayout.microring import AddDropMicroring,AddDropMicroringFlat
from splayout.polygon import Polygon
from splayout.quarbend import QuarBend,AQuarBend
from splayout.Selfdefinecomponent import MAKE_COMPONENT
from splayout.taper import Taper
from splayout.text import Text
from splayout.utils import *
from splayout.waveguide import Waveguide, ArbitraryAngleWaveguide
from splayout.sbend import SBend,ASBend
from splayout.filledpattern import Circle,Rectangle
from splayout.fdtdapi import FDTDSimulation
from splayout.modeapi import MODESimulation
from splayout.BinaryBatAlgorithm import BinaryBatAlgorithm
from splayout.DirectBinarySearchAlgorithm import DirectBianrySearchAlgorithm
from splayout.pixelsregion import RectanglePixelsRegion,CirclePixelsRegion
from splayout.ShapeOptRegion2D import ShapeOptRegion2D
from splayout.ShapeOptRegion3D import ShapeOptRegion3D
from splayout.TopologyOptRegion2D import TopologyOptRegion2D
from splayout.TopologyOptRegion3D import TopologyOptRegion3D
from splayout.AdjointForShapeOpt import AdjointForShapeOpt
from splayout.AdjointForTO import AdjointForTO
from splayout.BinaryParticleSwarmAlgorithm import BinaryParitcleSwarmAlgorithm
from splayout.BinaryGeneticAlgorithm import BinaryGeneticAlgorithm