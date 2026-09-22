"""
Database Seeder for Mining Supply Chain Digital Twin.
Populates normalized tables with realistic underground mining data, equipment,
critical BOM spare parts, suppliers, baseline inventories, scenarios, and strategies.
"""
import logging
import json
from datetime import datetime, timedelta
import hashlib
from database.connection import get_db_session, create_all_tables
from database.models import (
    Rol, Usuario, Mina, NivelMina, ZonaMina, TipoEquipo, Equipo,
    FallaEquipo, Mantenimiento, CategoriaRepuesto, Repuesto, BOMEquipo,
    Inventario, MovimientoInventario, Proveedor, ProveedorRepuesto,
    HistorialLeadTime, Transportista, Ruta, Envio, OrdenCompra,
    OrdenCompraDetalle, Recepcion, DigitalTwinState, Escenario,
    EstrategiaResiliencia, PruebaEstadistica
)

logger = logging.getLogger("mining_dt.seeder")

def hash_password(password: str) -> str:
    """Simple SHA256 / PBKDF2 hash for standalone compatibility."""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database(force: bool = False):
    create_all_tables()
    session = get_db_session()
    
    try:
        # Check if already seeded
        existing_mina = session.query(Mina).first()
        if existing_mina and not force:
            logger.info("Database already seeded. Skipping seed.")
            return True
        
        logger.info("Seeding database with realistic underground mining data...")
        
        # 1. Roles & Users
        roles_data = [
            ("ADMIN", "Acceso completo al sistema, configuración y usuarios"),
            ("INVESTIGADOR", "Acceso a datasets, EDA, Machine Learning, simulaciones y estadística"),
            ("OPERADOR", "Acceso a equipos, inventarios, órdenes y estado de la mina")
        ]
        roles_dict = {}
        for r_name, r_desc in roles_data:
            rol = session.query(Rol).filter_by(nombre=r_name).first()
            if not rol:
                rol = Rol(nombre=r_name, descripcion=r_desc)
                session.add(rol)
                session.flush()
            roles_dict[r_name] = rol
            
        users_data = [
            ("admin", "admin@minera.com", "admin123", "Sofia Contreras", "ADMIN"),
            ("investigador", "researcher@minadigitaltwin.com", "investigador123", "Dr. Investigador Senior", "INVESTIGADOR"),
            ("operador", "operator@minadigitaltwin.com", "operador123", "Jefe de Mantenimiento y Logística", "OPERADOR")
        ]
        for u_name, u_email, u_pass, u_full, r_name in users_data:
            if not session.query(Usuario).filter_by(username=u_name).first():
                user = Usuario(
                    username=u_name,
                    email=u_email,
                    password_hash=hash_password(u_pass),
                    nombre_completo=u_full,
                    rol_id=roles_dict[r_name].id
                )
                session.add(user)
        session.flush()

        # 2. Mina y Topología Subterránea
        mina = Mina(
            nombre="Mina Subterránea Titán Andino",
            codigo="MINA-TITAN",
            metodo_explotacion="Sublevel Stoping con Relleno Cementado",
            ubicacion="Cordillera de los Andes, 4,200 msnm",
            latitud=-11.854,
            longitud=-76.221,
            produccion_diaria_tpd=6500.0,
            costo_downtime_hora_usd=14500.0
        )
        session.add(mina)
        session.flush()

        niveles_data = [
            ("Nivel -120m", -120.0, "Nivel de Transporte Intermedio y Taller Superficial"),
            ("Nivel -240m", -240.0, "Nivel Principal de Producción y Taller Subterráneo Mecánico"),
            ("Nivel -360m", -360.0, "Nivel de Extracción Activa y Estación de Bombeo Principal"),
            ("Nivel -480m", -480.0, "Nivel de Avance en Profundidad y Ventilación Secundaria")
        ]
        niveles_dict = {}
        for n_name, cota, desc in niveles_data:
            nivel = NivelMina(mina_id=mina.id, nombre=n_name, cota_z=cota, descripcion=desc)
            session.add(nivel)
            session.flush()
            niveles_dict[n_name] = nivel

        zonas_data = [
            ("Almacén Central Superficie", "Nivel -120m", "ALMACEN", 0.0, 0.0, -120.0),
            ("Taller Mecánico Subterráneo N-240", "Nivel -240m", "TALLER", 150.0, 80.0, -240.0),
            ("Frente de Avance 240-Norte", "Nivel -240m", "PRODUCCION", 320.0, 140.0, -240.0),
            ("Estación Principal de Bombeo N-360", "Nivel -360m", "DRENAJE", 80.0, -110.0, -360.0),
            ("Cámara de Ventilación Axial Sur", "Nivel -360m", "VENTILACION", -200.0, -90.0, -360.0),
            ("Frente de Perforación 480-Oeste", "Nivel -480m", "PRODUCCION", -140.0, 260.0, -480.0)
        ]
        zonas_dict = {}
        for z_name, n_name, z_tipo, x, y, z in zonas_data:
            zona = ZonaMina(
                nivel_id=niveles_dict[n_name].id,
                nombre=z_name,
                tipo=z_tipo,
                coordenada_x=x,
                coordenada_y=y,
                coordenada_z=z
            )
            session.add(zona)
            session.flush()
            zonas_dict[z_name] = zona

        # 3. Tipos de Equipos
        tipos_data = [
            ("Scooptram (LHD)", "CARGUIO_TRANSPORTE", "Cargador frontal de bajo perfil para minería subterránea", 6500.0),
            ("Jumbo de Perforación", "PERFORACION", "Equipo electrohidráulico para perforación de frentes", 7200.0),
            ("Ventilador Axial Principal", "SERVICIOS_MINA", "Sistema de ventilación forzada primaria de interior mina", 14000.0),
            ("Bomba de Desagüe Multietapa", "SERVICIOS_MINA", "Bomba centrífuga de alta presión para desagüe de mina", 11500.0),
            ("Shovel / Pala de Carguío", "CARGUIO_TRANSPORTE", "Pala subterránea de alta capacidad", 8000.0),
            ("Perforadora Long Hole", "PERFORACION", "Perforadora de tiros largos para explotación por subniveles", 6800.0),
            ("Compresor Estacionario", "SERVICIOS_MINA", "Suministro de aire comprimido a redes subterráneas", 5000.0),
            ("Faja Transportadora (Conveyor)", "CARGUIO_TRANSPORTE", "Sistema continuo de evacuación de mineral chancado", 9500.0)
        ]
        tipos_dict = {}
        for t_nom, t_cat, t_desc, t_costo in tipos_data:
            t = TipoEquipo(nombre=t_nom, categoria=t_cat, descripcion=t_desc, costo_parada_hora_usd=t_costo)
            session.add(t)
            session.flush()
            tipos_dict[t_nom] = t

        # 4. Flota de Equipos Subterráneos (33 Equipos)
        equipos_seed = [
            # Scooptrams
            ("ST-01", "Scooptram CAT R1700K #01", "Scooptram (LHD)", "R1700K", "Caterpillar", "Taller Mecánico Subterráneo N-240", "OPERATIVO", 280.0, 14.0, 3200.0, 150.0, 80.0, -240.0),
            ("ST-02", "Scooptram CAT R1700K #02", "Scooptram (LHD)", "R1700K", "Caterpillar", "Frente de Avance 240-Norte", "OPERATIVO", 260.0, 16.0, 4100.0, 300.0, 120.0, -240.0),
            ("ST-03", "Scooptram Sandvik LH517i #03", "Scooptram (LHD)", "LH517i", "Sandvik", "Frente de Perforación 480-Oeste", "FALLADO", 220.0, 22.0, 5800.0, -120.0, 240.0, -480.0),
            ("ST-04", "Scooptram Sandvik LH517i #04", "Scooptram (LHD)", "LH517i", "Sandvik", "Frente de Avance 240-Norte", "OPERATIVO", 250.0, 15.0, 2900.0, 280.0, 110.0, -240.0),
            ("ST-05", "Scooptram Epiroc ST14 #05", "Scooptram (LHD)", "Scooptram ST14", "Epiroc", "Nivel -360m", "OPERATIVO", 270.0, 17.0, 3500.0, 50.0, -80.0, -360.0),
            ("ST-06", "Scooptram Epiroc ST14 #06", "Scooptram (LHD)", "Scooptram ST14", "Epiroc", "Nivel -360m", "MANTENIMIENTO", 240.0, 18.0, 4800.0, 60.0, -90.0, -360.0),
            ("ST-07", "Scooptram CAT R1300G #07", "Scooptram (LHD)", "R1300G", "Caterpillar", "Nivel -480m", "OPERATIVO", 290.0, 12.0, 2100.0, -100.0, 210.0, -480.0),
            ("ST-08", "Scooptram Sandvik LH410 #08", "Scooptram (LHD)", "LH410", "Sandvik", "Nivel -120m", "OPERATIVO", 310.0, 11.0, 1800.0, 20.0, 30.0, -120.0),
            
            # Jumbos
            ("JUM-01", "Jumbo Sandvik DD422i #01", "Jumbo de Perforación", "DD422i", "Sandvik", "Frente de Avance 240-Norte", "OPERATIVO", 210.0, 19.0, 3900.0, 340.0, 150.0, -240.0),
            ("JUM-02", "Jumbo Sandvik DD422i #02", "Jumbo de Perforación", "DD422i", "Sandvik", "Frente de Perforación 480-Oeste", "FALLADO", 190.0, 24.0, 4700.0, -150.0, 270.0, -480.0),
            ("JUM-03", "Jumbo Epiroc Boomer M2C #03", "Jumbo de Perforación", "Boomer M2C", "Epiroc", "Frente de Avance 240-Norte", "OPERATIVO", 230.0, 16.0, 3300.0, 310.0, 130.0, -240.0),
            ("JUM-04", "Jumbo Epiroc Boomer M2C #04", "Jumbo de Perforación", "Boomer M2C", "Epiroc", "Nivel -360m", "OPERATIVO", 225.0, 18.0, 3600.0, 70.0, -100.0, -360.0),
            ("JUM-05", "Jumbo Resemin Bolter 88 #05", "Jumbo de Perforación", "Bolter 88", "Resemin", "Nivel -240m", "OPERATIVO", 240.0, 15.0, 2800.0, 180.0, 90.0, -240.0),
            ("JUM-06", "Jumbo Sandvik DT820 #06", "Jumbo de Perforación", "DT820", "Sandvik", "Nivel -480m", "MANTENIMIENTO", 205.0, 21.0, 5200.0, -110.0, 230.0, -480.0),

            # Ventiladores Axiales Principales
            ("FAN-01", "Ventilador Principal Alphair V-101", "Ventilador Axial Principal", "Alphair 101-AM", "Alphair", "Cámara de Ventilación Axial Sur", "OPERATIVO", 850.0, 36.0, 12400.0, -200.0, -90.0, -360.0),
            ("FAN-02", "Ventilador Principal Alphair V-102", "Ventilador Axial Principal", "Alphair 101-AM", "Alphair", "Cámara de Ventilación Axial Sur", "OPERATIVO", 820.0, 38.0, 11800.0, -210.0, -85.0, -360.0),
            ("FAN-03", "Ventilador Howden N-240 V-201", "Ventilador Axial Principal", "Howden Mine Master", "Howden", "Nivel -240m", "OPERATIVO", 780.0, 42.0, 9500.0, 120.0, 40.0, -240.0),
            ("FAN-04", "Ventilador Zitron N-480 V-401", "Ventilador Axial Principal", "Zitron Z-Mine 250", "Zitron", "Nivel -480m", "OPERATIVO", 750.0, 40.0, 8900.0, -80.0, 180.0, -480.0),

            # Bombas de Desagüe
            ("PMP-01", "Bomba Principal Sulzer MSD-01", "Bomba de Desagüe Multietapa", "Sulzer MSD 6x8", "Sulzer", "Estación Principal de Bombeo N-360", "OPERATIVO", 550.0, 26.0, 7800.0, 80.0, -110.0, -360.0),
            ("PMP-02", "Bomba Principal Sulzer MSD-02", "Bomba de Desagüe Multietapa", "Sulzer MSD 6x8", "Sulzer", "Estación Principal de Bombeo N-360", "OPERATIVO", 520.0, 28.0, 8200.0, 85.0, -105.0, -360.0),
            ("PMP-03", "Bomba Flygt 2400 Sumergible #03", "Bomba de Desagüe Multietapa", "Flygt 2400", "Xylem/Flygt", "Nivel -480m", "OPERATIVO", 480.0, 18.0, 6100.0, -130.0, 250.0, -480.0),
            ("PMP-04", "Bomba Flygt 2400 Sumergible #04", "Bomba de Desagüe Multietapa", "Flygt 2400", "Xylem/Flygt", "Nivel -480m", "OPERATIVO", 470.0, 19.0, 5900.0, -135.0, 245.0, -480.0),
            ("PMP-05", "Bomba Weir Minerals Multiflo #05", "Bomba de Desagüe Multietapa", "Multiflo MF420", "Weir Minerals", "Nivel -240m", "OPERATIVO", 510.0, 22.0, 6700.0, 160.0, 70.0, -240.0),
            ("PMP-06", "Bomba Weir Minerals Multiflo #06", "Bomba de Desagüe Multietapa", "Multiflo MF420", "Weir Minerals", "Nivel -360m", "OPERATIVO", 530.0, 21.0, 6400.0, 95.0, -95.0, -360.0),

            # Shovels
            ("SHV-01", "Pala Eléctrica Marion 301 #01", "Shovel / Pala de Carguío", "Marion 301 Sub", "Marion/CAT", "Nivel -240m", "OPERATIVO", 380.0, 28.0, 8400.0, 260.0, 100.0, -240.0),
            ("SHV-02", "Pala Eléctrica Marion 301 #02", "Shovel / Pala de Carguío", "Marion 301 Sub", "Marion/CAT", "Nivel -360m", "OPERATIVO", 360.0, 30.0, 8900.0, 110.0, -70.0, -360.0),

            # Perforadoras Long Hole
            ("LHD-P01", "Perforadora Long Hole Simba S7 #01", "Perforadora Long Hole", "Simba S7D", "Epiroc", "Frente de Perforación 480-Oeste", "OPERATIVO", 215.0, 18.0, 4200.0, -160.0, 280.0, -480.0),
            ("LHD-P02", "Perforadora Long Hole Sandvik DL421 #02", "Perforadora Long Hole", "DL421", "Sandvik", "Frente de Avance 240-Norte", "OPERATIVO", 225.0, 17.0, 3700.0, 350.0, 160.0, -240.0),

            # Compresores Estacionarios
            ("CMP-01", "Compresor Atlas Copco GA250 #01", "Compresor Estacionario", "GA 250 VSD", "Atlas Copco", "Almacén Central Superficie", "OPERATIVO", 920.0, 14.0, 14200.0, -10.0, -20.0, -120.0),
            ("CMP-02", "Compresor Atlas Copco GA250 #02", "Compresor Estacionario", "GA 250 VSD", "Atlas Copco", "Almacén Central Superficie", "OPERATIVO", 900.0, 15.0, 13800.0, 0.0, -25.0, -120.0),
            ("CMP-03", "Compresor Sullair TS32 #03", "Compresor Estacionario", "TS32S-350", "Sullair", "Taller Mecánico Subterráneo N-240", "OPERATIVO", 880.0, 16.0, 12600.0, 140.0, 65.0, -240.0),

            # Fajas Transportadoras
            ("CV-01", "Conveyor Principal Evacuación CV-101", "Faja Transportadora (Conveyor)", "Conveyor 42in HP", "Fenner Dunlop", "Nivel -240m", "OPERATIVO", 640.0, 32.0, 11500.0, 200.0, 50.0, -240.0),
            ("CV-02", "Conveyor Alimentación Triturador CV-202", "Faja Transportadora (Conveyor)", "Conveyor 36in Heavy", "Continental", "Nivel -360m", "OPERATIVO", 620.0, 34.0, 10800.0, 130.0, -60.0, -360.0)
        ]
        equipos_dict = {}
        for cod, nom, tipo_nom, mod, fab, zon_nom, est, mtbf, mttr, h_op, px, py, pz in equipos_seed:
            zona_obj = zonas_dict.get(zon_nom)
            eq = Equipo(
                codigo=cod,
                nombre=nom,
                tipo_equipo_id=tipos_dict[tipo_nom].id,
                mina_id=mina.id,
                zona_id=zona_obj.id if zona_obj else None,
                modelo=mod,
                fabricante=fab,
                estado=est,
                mtbf_horas=mtbf,
                mttr_horas=mttr,
                horas_operacion=h_op,
                posicion_x=px,
                posicion_y=py,
                posicion_z=pz,
                ultima_falla=datetime.utcnow() - timedelta(days=12) if est == "FALLADO" else None,
                proximo_mantenimiento=datetime.utcnow() + timedelta(days=7)
            )
            session.add(eq)
            session.flush()
            equipos_dict[cod] = eq

        # 5. Categorías y Repuestos Críticos (Sin tornillos ni consumibles menores)
        categorias_data = [
            ("Hidráulica de Alta Presión", "Bombas de pistones axiales, motores hidráulicos y válvulas proporcionales"),
            ("Transmisión y Tren de Potencia", "Convertidores de par, diferenciales y transmisiones Powershift"),
            ("Electrónica y Control ECM", "Módulos ECM/ADEM, controladores PLC industriales y sensores críticos"),
            ("Ventilación y Flujo de Aire", "Rotores axiales balanceados dinámicamente, alabes de paso variable"),
            ("Desagüe y Bombeo de Relaves", "Impulsores de cromo alto, sellos mecánicos dobles de carburo"),
            ("Perforación y Rotación", "Cabezales de rotación de perforadora, amortiguadores y cilindros de avance")
        ]
        cat_dict = {}
        for c_nom, c_desc in categorias_data:
            c = CategoriaRepuesto(nombre=c_nom, descripcion=c_desc, es_critica=1)
            session.add(c)
            session.flush()
            cat_dict[c_nom] = c

        repuestos_data = [
            # Código, Nombre, Categoría, Costo USD, Lead Time días, Lambda falla, Stock act, min, max, ss, rop, 3d, rep_local
            ("PUMP-HYD-A4VG", "Bomba Hidráulica de Pistones Axiales Rexroth A4VG125", "Hidráulica de Alta Presión", 11500.0, 125.0, 0.042, 1, 1, 4, 1, 2, 0, 1),
            ("SEAL-MECH-SULZ", "Sello Mecánico Doble Carburo de Silicio Sulzer MSD", "Desagüe y Bombeo de Relaves", 3200.0, 95.0, 0.038, 2, 2, 6, 2, 3, 1, 0),
            ("ECM-CAT-ADEM4", "Módulo de Control Electrónico ADEM A4 Caterpillar", "Electrónica y Control ECM", 14800.0, 150.0, 0.025, 0, 1, 3, 1, 2, 0, 0),
            ("CYL-FEED-SANDV", "Cilindro Hidráulico de Avance Sandvik DD422", "Perforación y Rotación", 8400.0, 110.0, 0.048, 1, 1, 4, 1, 2, 1, 1),
            ("ROTOR-AX-ALPH", "Rotor Impulsor Balanceado Dinámico Alphair 101-AM", "Ventilación y Flujo de Aire", 24500.0, 180.0, 0.018, 1, 1, 3, 1, 2, 0, 1),
            ("CONV-TRQ-DANA", "Convertidor de Torque Powershift Dana Spicer T40000", "Transmisión y Tren de Potencia", 18200.0, 140.0, 0.032, 1, 1, 3, 1, 2, 0, 1),
            ("VALV-SLUR-HIGH", "Válvula Esférica de Lodos y Alta Presión 8in 600#", "Desagüe y Bombeo de Relaves", 5900.0, 105.0, 0.040, 2, 2, 6, 2, 3, 1, 0),
            ("HEAD-ROT-ATLAS", "Cabezal de Rotación Perforadora Atlas Copco COP 1838", "Perforación y Rotación", 19800.0, 135.0, 0.035, 0, 1, 3, 1, 2, 0, 1),
            ("PLC-MASTER-SIEM", "Controlador PLC Modular de Seguridad Siemens S7-1500F", "Electrónica y Control ECM", 9200.0, 130.0, 0.022, 1, 1, 4, 1, 2, 0, 0),
            ("RED-PLAN-FLEND", "Reductor Planetario de Faja Transportadora Flender 350kW", "Transmisión y Tren de Potencia", 21000.0, 160.0, 0.020, 1, 1, 3, 1, 2, 0, 1)
        ]
        repuestos_dict = {}
        for cod, nom, c_nom, costo, lt, lmb, s_act, s_min, s_max, ss, rop, p3d, prl in repuestos_data:
            rep = Repuesto(
                codigo=cod,
                nombre=nom,
                categoria_id=cat_dict[c_nom].id,
                criticidad="CRITICA",
                costo_unitario_usd=costo,
                lead_time_promedio_dias=lt,
                tasa_falla_lambda=lmb,
                mtbf_horas=round(1000.0 / lmb, 1),
                stock_actual=s_act,
                stock_minimo=s_min,
                stock_maximo=s_max,
                stock_seguridad=ss,
                punto_reorden=rop,
                consumo_mensual_promedio=round(lmb * 24.0, 2),
                permite_impresion_3d=p3d,
                permite_reparacion_local=prl
            )
            session.add(rep)
            session.flush()
            repuestos_dict[cod] = rep

            # Inventario asociado
            inv = Inventario(
                repuesto_id=rep.id,
                almacen="ALMACEN_CENTRAL_SUPERFICIE",
                cantidad_disponible=s_act,
                cantidad_reservada=1 if s_act == 0 else 0,
                cantidad_en_transito=1 if s_act <= rop else 0,
                ubicacion_estante=f"RACK-CRIT-{rep.id:02d}",
                valor_total_inventario_usd=s_act * costo
            )
            session.add(inv)

        # 6. BOM (Bill of Materials) para Equipos
        bom_seed = [
            ("ST-01", "PUMP-HYD-A4VG", "Sistema Hidráulico Principal", 1, "VITAL"),
            ("ST-01", "CONV-TRQ-DANA", "Tren de Potencia / Transmisión", 1, "VITAL"),
            ("ST-01", "ECM-CAT-ADEM4", "Control Electrónico de Inyección y Motor", 1, "VITAL"),
            ("ST-02", "PUMP-HYD-A4VG", "Sistema Hidráulico Principal", 1, "VITAL"),
            ("ST-02", "CONV-TRQ-DANA", "Tren de Potencia / Transmisión", 1, "VITAL"),
            ("ST-03", "PUMP-HYD-A4VG", "Sistema Hidráulico Principal", 1, "VITAL"),
            ("ST-03", "ECM-CAT-ADEM4", "Control Electrónico de Inyección", 1, "VITAL"),
            ("JUM-01", "CYL-FEED-SANDV", "Sistema de Viga de Avance", 2, "VITAL"),
            ("JUM-01", "PUMP-HYD-A4VG", "Central Hidráulica de Perforación", 1, "VITAL"),
            ("JUM-02", "CYL-FEED-SANDV", "Sistema de Viga de Avance", 2, "VITAL"),
            ("JUM-02", "HEAD-ROT-ATLAS", "Drifter de Percusión / Rotación", 2, "VITAL"),
            ("FAN-01", "ROTOR-AX-ALPH", "Ensamble Rotor / Alabes Aerodinámicos", 1, "VITAL"),
            ("FAN-01", "PLC-MASTER-SIEM", "Tablero de Control y Monitoreo VFD", 1, "VITAL"),
            ("FAN-02", "ROTOR-AX-ALPH", "Ensamble Rotor / Alabes Aerodinámicos", 1, "VITAL"),
            ("PMP-01", "SEAL-MECH-SULZ", "Cámara de Sellado de Alta Presión", 2, "VITAL"),
            ("PMP-01", "VALV-SLUR-HIGH", "Manifold de Descarga a Superficie", 1, "ESCENCIAL"),
            ("PMP-02", "SEAL-MECH-SULZ", "Cámara de Sellado de Alta Presión", 2, "VITAL"),
            ("PMP-02", "VALV-SLUR-HIGH", "Manifold de Descarga a Superficie", 1, "ESCENCIAL"),
            ("CV-01", "RED-PLAN-FLEND", "Unidad Motriz Principal", 1, "VITAL"),
            ("CV-02", "RED-PLAN-FLEND", "Unidad Motriz Principal", 1, "VITAL")
        ]
        for eq_cod, rep_cod, sub, cant, crit in bom_seed:
            if eq_cod in equipos_dict and rep_cod in repuestos_dict:
                bom = BOMEquipo(
                    equipo_id=equipos_dict[eq_cod].id,
                    repuesto_id=repuestos_dict[rep_cod].id,
                    subsistema=sub,
                    cantidad=cant,
                    criticidad_subsistema=crit
                )
                session.add(bom)

        # 7. Proveedores y Asignación de Cuotas (SDI)
        proveedores_data = [
            ("Hydraulics Global OEM GmbH", "SUP-HYD-DE", "Alemania", 0, 0.94, 15, 120.0, 18.0, "MEDIO", "DISPONIBLE"),
            ("Nordic Mining Spares AB", "SUP-NOR-SE", "Suecia", 0, 0.95, 20, 135.0, 14.0, "BAJO", "DISPONIBLE"),
            ("Trans-Power Technologies Inc", "SUP-PWR-US", "Estados Unidos", 0, 0.89, 12, 110.0, 22.0, "MEDIO", "DISPONIBLE"),
            ("TecnoMin Andina Maestranza SAC", "SUP-LOC-PE", "Perú / Región Andina", 1, 0.84, 8, 14.0, 6.0, "BAJO", "DISPONIBLE"),
            ("Additive Metal Mining Solutions", "SUP-3D-MET", "Chile / Laboratorio 3D", 1, 0.91, 10, 4.0, 2.0, "BAJO", "DISPONIBLE")
        ]
        prov_dict = {}
        for nom, cod, pais, es_loc, conf, cap, lt, var_lt, n_riesgo, est in proveedores_data:
            p = Proveedor(
                nombre=nom,
                codigo=cod,
                pais_origen=pais,
                es_local=es_loc,
                confiabilidad_score=conf,
                capacidad_mensual_unidades=cap,
                lead_time_base_dias=lt,
                variabilidad_lead_time_dias=var_lt,
                nivel_riesgo=n_riesgo,
                estado=est
            )
            session.add(p)
            session.flush()
            prov_dict[cod] = p

        # Relación Proveedor - Repuesto (Cuotas para SDI y Single Source Supplier Risk)
        prov_rep_seed = [
            # Bombas hidráulicas: 85% Alemania (monopólico), 15% Taller Local
            ("SUP-HYD-DE", "PUMP-HYD-A4VG", 11500.0, 120.0, 85.0, 1),
            ("SUP-LOC-PE", "PUMP-HYD-A4VG", 8800.0, 18.0, 15.0, 0),
            # Sellos mecánicos: 90% Suecia, 10% Local 3D
            ("SUP-NOR-SE", "SEAL-MECH-SULZ", 3200.0, 95.0, 90.0, 1),
            ("SUP-3D-MET", "SEAL-MECH-SULZ", 2400.0, 5.0, 10.0, 0),
            # ECM ADEM4: 100% USA (Single Source puro)
            ("SUP-PWR-US", "ECM-CAT-ADEM4", 14800.0, 150.0, 100.0, 1),
            # Cilindros Sandvik: 85% Suecia, 15% Local
            ("SUP-NOR-SE", "CYL-FEED-SANDV", 8400.0, 110.0, 85.0, 1),
            ("SUP-LOC-PE", "CYL-FEED-SANDV", 6500.0, 16.0, 15.0, 0),
            # Rotor Alphair: 90% Alemania, 10% Local
            ("SUP-HYD-DE", "ROTOR-AX-ALPH", 24500.0, 180.0, 90.0, 1),
            ("SUP-LOC-PE", "ROTOR-AX-ALPH", 17000.0, 25.0, 10.0, 0),
            # Convertidor Torque: 100% USA (Single Source)
            ("SUP-PWR-US", "CONV-TRQ-DANA", 18200.0, 140.0, 100.0, 1),
            # Válvulas lodo: 75% Suecia, 25% Local 3D
            ("SUP-NOR-SE", "VALV-SLUR-HIGH", 5900.0, 105.0, 75.0, 1),
            ("SUP-3D-MET", "VALV-SLUR-HIGH", 4800.0, 4.0, 25.0, 0),
            # Cabezal rotación: 100% Suecia
            ("SUP-NOR-SE", "HEAD-ROT-ATLAS", 19800.0, 135.0, 100.0, 1),
            # PLC Siemens: 100% Alemania
            ("SUP-HYD-DE", "PLC-MASTER-SIEM", 9200.0, 130.0, 100.0, 1),
            # Reductor Flender: 100% Alemania
            ("SUP-HYD-DE", "RED-PLAN-FLEND", 21000.0, 160.0, 100.0, 1)
        ]
        for p_cod, r_cod, costo, lt, cuota, prim in prov_rep_seed:
            pr = ProveedorRepuesto(
                proveedor_id=prov_dict[p_cod].id,
                repuesto_id=repuestos_dict[r_cod].id,
                costo_unitario_usd=costo,
                lead_time_dias=lt,
                cuota_suministro_pct=cuota,
                es_proveedor_primario=prim
            )
            session.add(pr)

        # 8. Escenarios Preconfigurados de Resiliencia
        escenarios_data = [
            ("ESC-01", "Cierre de Frontera Geopolítico", "CIERRE_FRONTERA", "Bloqueo fronterizo e interrupción portuaria severa. Incremento del lead time internacional en +200% por 90 días.", 90, 3.0, 1.0, 100.0, 0),
            ("ESC-02", "Falla Catastrófica de Proveedor Único", "FALLA_PROVEEDOR_UNICO", "Quiebra o paro laboral del fabricante principal alemán durante 120 días con 0% de disponibilidad.", 120, 1.0, 1.0, 0.0, 0),
            ("ESC-03", "Demanda Extrema por Desgaste Severo", "DEMANDA_EXTREMA", "Condiciones hidrogeológicas extremas y roca abrasiva que duplican la tasa de falla (+200%).", 180, 1.0, 2.0, 100.0, 0),
            ("ESC-04", "Activación de Impresión 3D In-Situ", "IMPRESION_3D_LOCAL", "Disrupción logística mitigada mediante celda de manufactura aditiva metálica in-situ con lead time de 3-4 días.", 365, 1.0, 1.0, 100.0, 1)
        ]
        for cod, nom, tipo, desc, dur, f_lt, f_tf, d_crit, c_3d in escenarios_data:
            esc = Escenario(
                codigo=cod,
                nombre=nom,
                tipo=tipo,
                descripcion=desc,
                duracion_dias=dur,
                factor_lead_time=f_lt,
                factor_tasa_falla=f_tf,
                disponibilidad_proveedor_critico_pct=d_crit,
                capacidad_impresion_3d_activa=c_3d
            )
            session.add(esc)

        # 9. Estrategias de Resiliencia
        estrategias_data = [
            ("ESTRATEGIA_A", "Estrategia A — Situación Actual (Baseline)", "Política tradicional 'Just-in-Time' con proveedor único extranjero y stock de seguridad mínimo.", 0.0, 0, 100.0, 0, 0),
            ("ESTRATEGIA_B", "Estrategia B — Expansión de Stock de Seguridad", "Incremento del buffer de seguridad en +100% para amortiguar fluctuaciones de lead time.", 100.0, 0, 100.0, 0, 0),
            ("ESTRATEGIA_C", "Estrategia C — Dual Sourcing Equilibrado", "Diversificación contractual dividiendo compras 65% proveedor global y 35% proveedor regional/nacional.", 0.0, 1, 65.0, 0, 0),
            ("ESTRATEGIA_D", "Estrategia D — Reparación y Reacondicionamiento Local", "Convenio con maestranza y taller especializado para recuperación de componentes mecánicos.", 20.0, 0, 100.0, 1, 0),
            ("ESTRATEGIA_E", "Estrategia E — Manufactura Aditiva 3D Local", "Impresión in-situ de repuestos poliméricos y metálicos para componentes críticos seleccionados.", 0.0, 0, 100.0, 0, 1),
            ("ESTRATEGIA_HIBRIDA", "Estrategia Híbrida — Dual Sourcing + Impresión 3D", "Combinación sinérgica de Dual Sourcing regional y fabricación aditiva local.", 30.0, 1, 65.0, 1, 1)
        ]
        for cod, nom, desc, s_ss, dual, cuota, rep_loc, m3d in estrategias_data:
            est = EstrategiaResiliencia(
                codigo=cod,
                nombre=nom,
                descripcion=desc,
                incremento_stock_seguridad_pct=s_ss,
                dual_sourcing_activo=dual,
                cuota_dual_sourcing_primario_pct=cuota,
                reparacion_local_activa=rep_loc,
                manufactura_3d_activa=m3d
            )
            session.add(est)

        # 10. Pruebas Estadísticas Registradas
        pruebas_data = [
            ("FRIEDMAN", "COMPARACION_MODELOS", "Prueba no paramétrica para contrastar diferencias globales de rendimiento entre los 5 modelos sobre los 5 folds.", "H0: No existen diferencias de desempeño entre los modelos.", "H1: Al menos dos modelos presentan diferencias estadísticamente significativas."),
            ("WILCOXON_HOLM", "COMPARACION_MODELOS", "Comparaciones pareadas no paramétricas post-hoc con corrección secuencial de Holm-Bonferroni para controlar FWER.", "H0: El par de modelos tiene idéntica distribución de score.", "H1: El modelo superior supera significativamente al comparado."),
            ("BOOTSTRAP_10K", "RESILIENCIA_DOWNTIME", "Re-muestreo con reemplazo (10,000 réplicas) para estimar intervalos de confianza al 95% de la diferencia de métricas.", "H0: La diferencia promedio es igual a cero.", "H1: La diferencia promedio difiere de cero en el IC 95%."),
            ("KOLMOGOROV_SMIRNOV", "VALIDACION_DT", "Comparación de distribuciones empíricas acumuladas entre datos reales y datos simulados del Gemelo Digital.", "H0: La muestra simulada proviene de la misma distribución que la real.", "H1: Las distribuciones simulada y real difieren significativamente."),
            ("MANN_WHITNEY_U", "RESILIENCIA_DOWNTIME", "Prueba de rangos de suma para verificar si la reducción de downtime entre estrategias es estadísticamente significativa.", "H0: El downtime con la estrategia resiliente no difiere del baseline.", "H1: El downtime se reduce significativamente con la estrategia propuesta."),
            ("SOBOL_SENSITIVITY", "SENSIBILIDAD", "Descomposición de varianza para calcular índices de primer orden (S1) y efectos totales (ST) de los factores de riesgo.", "H0: Los parámetros no aportan varianza explicativa al downtime.", "H1: Los parámetros explican fracciones medibles de la varianza total."),
            ("HIPOTESIS_H0_H1", "RESILIENCIA_DOWNTIME", "Evaluación formal de la hipótesis científica principal: Reducción de downtime >= 30% con p < 0.05.", "H0: El DT no identifica estrategias que reduzcan significativamente el downtime.", "H1: El DT identifica configuraciones que reducen el downtime en al menos 30% respecto a la situación actual.")
        ]
        for p_nom, p_cat, p_desc, p_h0, p_h1 in pruebas_data:
            p = PruebaEstadistica(
                nombre_prueba=p_nom,
                categoria=p_cat,
                descripcion=p_desc,
                hipotesis_nula_h0=p_h0,
                hipotesis_alternativa_h1=p_h1,
                nivel_significancia_alpha=0.05
            )
            session.add(p)

        # 11. Snapshot Inicial del Digital Twin State
        dt_state = DigitalTwinState(
            nombre_estado="ESTADO_ACTUAL_OPERATIVO_MINA",
            origen_datos="MINA_FISICA",
            equipos_total=33,
            equipos_operativos=29,
            equipos_mantenimiento=2,
            equipos_fallados=2,
            equipos_fuera_servicio=0,
            disponibilidad_flota_pct=87.88,
            stock_total_piezas=11,
            stock_critico_piezas=11,
            stockouts_activos=2,
            fill_rate_pct=81.2,
            nivel_servicio_pct=84.5,
            lead_time_promedio_dias=132.0,
            ordenes_pendientes=4,
            proveedores_en_riesgo=2,
            mtbf_promedio_horas=245.0,
            mttr_promedio_horas=18.4,
            downtime_acumulado_horas=420.0,
            perdida_produccion_usd=6090000.0,
            snapshot_json=json.dumps({"equipos_fallados": ["ST-03", "JUM-02"], "repuestos_en_quiebre": ["ECM-CAT-ADEM4", "HEAD-ROT-ATLAS"]}),
            notas="Estado inicial sincronizado de la flota y almacenes subterráneos."
        )
        session.add(dt_state)

        session.commit()
        logger.info("Database seeding completed successfully.")
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding database: {e}", exc_info=True)
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    seed_database(force=True)
