import streamlit as st
from pathlib import Path
import json
import numpy as np
from stl import mesh
import plotly.graph_objects as go
import pandas as pd
import io
import os

def load_3d_model(uploaded_file):
    """Load 3D model file (STL format) and return vertices and faces"""
    if uploaded_file is None:
        return None, None

    try:
        # Create a temporary file path
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)

        # Save the uploaded file temporarily
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load the mesh from the temporary file
        your_mesh = mesh.Mesh.from_file(temp_path)

        # Get vertices and create faces
        vertices = your_mesh.vectors.reshape(-1, 3)
        faces = np.arange(len(vertices)).reshape(-1, 3)

        # Clean up
        os.remove(temp_path)

        return vertices, faces

    except Exception as e:
        st.error(f"Error loading STL file: {str(e)}")
        # Clean up in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None, None

def display_3d_model(vertices, faces):
    """Create a 3D visualization using plotly"""
    if vertices is None or faces is None:
        return None

    # Calculate center of the model
    center = vertices.mean(axis=0)

    # Center the model at origin
    vertices = vertices - center

    # Scale the model to fit in a unit cube
    max_range = np.ptp(vertices, axis=0).max()
    if max_range != 0:  # Avoid division by zero
        vertices = vertices / max_range

    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color='lightblue',
            opacity=0.8,
            hoverinfo='none'
        )
    ])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        width=600,
        height=400,
        showlegend=False
    )
    return fig

def ensure_directories():
    """Create necessary directories"""
    for dir_name in ["projects", "temp"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

def main():
    st.set_page_config(layout="wide")
    st.title("Game Character Showcase")

    # Create necessary directories
    ensure_directories()


    st.info("Please ensure your STL files are less than 200MB each.")

    # model_cols = st.columns(1)

    # with model_cols[0]:
    st.subheader("Character Model")
    character_file = st.file_uploader("Upload Character Model (STL)", type=['stl'])
    if character_file is not None:
        try:
            vertices, faces = load_3d_model(character_file)
            if vertices is not None and faces is not None:
                fig = display_3d_model(vertices, faces)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                    st.text(f"Vertices: {len(vertices)}")
        except Exception as e:
            st.error(f"Failed to load model: {str(e)}")


    # Save project data
    project_name = None # Remove for your final version
    if st.button("Save Project"):
        if not project_name:
            st.error("Please enter a project name before saving.")
            return

        project_data = {} # Change with the required JSON structure

        # Save to JSON file
        try:
            with open(f"projects/{project_name.lower().replace(' ', '_')}.json", 'w') as f:
                json.dump(project_data, f, indent=4)
            st.success("Project saved successfully!")
        except Exception as e:
            st.error(f"Error saving project: {str(e)}")

if __name__ == "__main__":
    main()
