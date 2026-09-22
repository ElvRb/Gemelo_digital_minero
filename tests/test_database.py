"""
Unit tests for database models, normalized tables, and seeding.
"""
import pytest
from database.connection import create_all_tables, get_db_session
from database.seed.data_seeder import seed_database
from database.models import Equipo, Repuesto, Proveedor, BOMEquipo, Inventario
from backend.services.supply_chain_service import SupplyChainService

def test_database_creation_and_seeding():
    create_all_tables()
    seeded = seed_database(force=False)
    assert seeded is True

    session = get_db_session()
    try:
        equipos_count = session.query(Equipo).count()
        assert equipos_count == 33, f"Expected 33 underground machines, found {equipos_count}"

        repuestos_count = session.query(Repuesto).count()
        assert repuestos_count >= 10, f"Expected at least 10 critical parts, found {repuestos_count}"

        proveedores_count = session.query(Proveedor).count()
        assert proveedores_count >= 5, f"Expected at least 5 suppliers, found {proveedores_count}"

        bom_count = session.query(BOMEquipo).count()
        assert bom_count > 15, f"Expected BOM links, found {bom_count}"
    finally:
        session.close()

def test_supplier_dependency_index():
    sdi_data = SupplyChainService.calculate_supplier_dependency_index()
    assert len(sdi_data) >= 10
    
    # Check that at least one part is identified as Single Source Supplier Risk
    single_source_risks = [item for item in sdi_data if item["single_source_risk"] == "ALTO"]
    assert len(single_source_risks) > 0, "Should detect at least one single-source risk part"
