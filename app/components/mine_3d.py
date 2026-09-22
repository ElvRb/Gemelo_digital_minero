"""
3D Interactive Underground Mine Topology Visualizer using Plotly 3D.
Displays mining levels, shafts, maintenance bays, and equipment health status nodes.
"""
from typing import List, Dict, Any
import plotly.graph_objects as go
import numpy as np

def create_mine_3d_figure(equipment_data: List[Dict[str, Any]]) -> go.Figure:
    fig = go.Figure()

    # 1. Subterranean Depth Levels (Planes)
    levels = [
        {"name": "Nivel -120m (Superficie / Taller)", "z": -120.0, "color": "rgba(100, 116, 139, 0.15)"},
        {"name": "Nivel -240m (Producción Norte)", "z": -240.0, "color": "rgba(59, 130, 246, 0.15)"},
        {"name": "Nivel -360m (Estación de Bombeo)", "z": -360.0, "color": "rgba(16, 185, 129, 0.15)"},
        {"name": "Nivel -480m (Avance en Profundidad)", "z": -480.0, "color": "rgba(245, 158, 11, 0.15)"}
    ]

    for lvl in levels:
        x_grid = [-250, 400, 400, -250]
        y_grid = [-200, -200, 320, 320]
        z_grid = [lvl["z"]] * 4
        
        fig.add_trace(go.Mesh3d(
            x=x_grid,
            y=y_grid,
            z=z_grid,
            color=lvl["color"],
            opacity=0.35,
            name=lvl["name"],
            showlegend=False,
            hoverinfo="skip"
        ))

    # 2. Main Vertical Shaft (Pique Principal de Extracción)
    z_shaft = np.linspace(0, -480, 50)
    x_shaft = np.zeros(50)
    y_shaft = np.zeros(50)
    fig.add_trace(go.Scatter3d(
        x=x_shaft, y=y_shaft, z=z_shaft,
        mode="lines",
        line=dict(color="#334155", width=6, dash="dash"),
        name="Pique Vertical Principal",
        hoverinfo="text",
        text="Pique Principal de Extracción y Ventilación (0m a -480m)"
    ))

    # 3. Underground Equipment Nodes grouped by status
    status_colors = {
        "OPERATIVO": "#10b981", # Green
        "MANTENIMIENTO": "#f59e0b", # Amber
        "FALLADO": "#ef4444", # Red
        "FUERA_DE_SERVICIO": "#64748b" # Gray
    }

    for status, col in status_colors.items():
        subset = [e for e in equipment_data if e["estado"] == status]
        if not subset:
            continue

        xs = [e["posicion"]["x"] for e in subset]
        ys = [e["posicion"]["y"] for e in subset]
        zs = [e["posicion"]["z"] for e in subset]
        hover_texts = [
            f"<b>{e['codigo']} — {e['nombre']}</b><br>"
            f"Tipo: {e['tipo']}<br>"
            f"Estado: {e['estado']}<br>"
            f"Salud del Activo: {e.get('salud_pct', 90)}%<br>"
            f"MTBF: {e['mtbf_horas']} h | MTTR: {e['mttr_horas']} h<br>"
            f"Cota: Z = {e['posicion']['z']}m"
            for e in subset
        ]

        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="markers+text",
            marker=dict(size=8, color=col, symbol="diamond" if status == "FALLADO" else "circle", line=dict(color="#000000", width=1)),
            text=[e["codigo"] for e in subset],
            textposition="top center",
            textfont=dict(size=9, color="#1e293b"),
            hovertext=hover_texts,
            hoverinfo="text",
            name=f"{status} ({len(subset)})"
        ))

    fig.update_layout(
        showlegend=False,
        scene=dict(
            xaxis=dict(title="Coordenada Este (m)", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            yaxis=dict(title="Coordenada Norte (m)", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            zaxis=dict(title="Cota Profundidad Z (m)", backgroundcolor="#f1f5f9", gridcolor="#cbd5e1"),
            aspectmode="manual",
            aspectratio=dict(x=1.2, y=1.2, z=0.9),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.1))
        ),
        margin=dict(l=0, r=0, b=10, t=10),
        height=520
    )
    return fig
