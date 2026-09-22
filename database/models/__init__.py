"""Database models package aggregating all normalized tables for the Mining Digital Twin."""
from database.models.user import Usuario, Rol
from database.models.mine import Mina, NivelMina, ZonaMina
from database.models.equipment import TipoEquipo, Equipo, FallaEquipo, Mantenimiento
from database.models.spare_part import CategoriaRepuesto, Repuesto, BOMEquipo
from database.models.inventory import Inventario, MovimientoInventario
from database.models.supplier import Proveedor, ProveedorRepuesto, HistorialLeadTime
from database.models.logistics import (
    Transportista, Ruta, Envio, OrdenCompra, OrdenCompraDetalle, Recepcion, Reparacion
)
from database.models.digital_twin import DigitalTwinState
from database.models.simulation import (
    Escenario, EstrategiaResiliencia, ParametroSimulacion, Simulacion,
    CorridaSimulacion, ResultadoSimulacion
)
from database.models.ml import (
    DatasetModel, ExperimentoML, ModeloML, HiperparametroML, ResultadoCV
)
from database.models.statistics import (
    PruebaEstadistica, ResultadoEstadistico, Prediccion, Recomendacion
)

__all__ = [
    "Usuario", "Rol",
    "Mina", "NivelMina", "ZonaMina",
    "TipoEquipo", "Equipo", "FallaEquipo", "Mantenimiento",
    "CategoriaRepuesto", "Repuesto", "BOMEquipo",
    "Inventario", "MovimientoInventario",
    "Proveedor", "ProveedorRepuesto", "HistorialLeadTime",
    "Transportista", "Ruta", "Envio", "OrdenCompra", "OrdenCompraDetalle", "Recepcion", "Reparacion",
    "DigitalTwinState",
    "Escenario", "EstrategiaResiliencia", "ParametroSimulacion", "Simulacion",
    "CorridaSimulacion", "ResultadoSimulacion",
    "DatasetModel", "ExperimentoML", "ModeloML", "HiperparametroML", "ResultadoCV",
    "PruebaEstadistica", "ResultadoEstadistico", "Prediccion", "Recomendacion"
]
