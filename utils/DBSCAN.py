#!/usr/bin/env python
import sys
import os
import glob
import vtk
import numpy as np
from vtk.util import numpy_support
from sklearn.cluster import DBSCAN

########################################
# Generated code snippet for DBSCAN algo
########################################


def load_vtu(filename):
    """Load a VTU file and return the vtkUnstructuredGrid."""
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def write_vtu(data, filename):
    """Write the given vtkUnstructuredGrid to a VTU file."""
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()

def create_polydata_from_points(points_array, arrays_dict=None):
    """
    Create a vtkUnstructuredGrid from a NumPy array of points.
    Optionally, attach additional point data from arrays_dict.
    """
    numPts = points_array.shape[0]
    # Create vtkPoints and insert each point
    vtk_pts = vtk.vtkPoints()
    vtk_pts.SetNumberOfPoints(numPts)
    for i in range(numPts):
        vtk_pts.SetPoint(i, points_array[i])

    # Create a new vtkUnstructuredGrid and assign points
    ug = vtk.vtkUnstructuredGrid()
    ug.SetPoints(vtk_pts)

    # For each point, create a vertex cell (so that points are visible)
    for i in range(numPts):
        cell = vtk.vtkVertex()
        cell.GetPointIds().SetId(0, i)
        ug.InsertNextCell(cell.GetCellType(), cell.GetPointIds())

    # Optionally add arrays in arrays_dict (each should be a NumPy array with length numPts)
    if arrays_dict is not None:
        for name, arr in arrays_dict.items():
            vtk_arr = numpy_support.numpy_to_vtk(num_array=arr, deep=True, array_type=vtk.VTK_FLOAT)
            vtk_arr.SetName(name)
            ug.GetPointData().AddArray(vtk_arr)
        # Optionally, set an active scalar array (for example, cluster labels or concentration)
        if "DBSCAN_Labels" in arrays_dict:
            ug.GetPointData().SetActiveScalars("DBSCAN_Labels")
        elif "concentration" in arrays_dict:
            ug.GetPointData().SetActiveScalars("concentration")

    return ug

def process_file(infile, outfile):
    # Load input VTU file
    polydata = load_vtu(infile)
    points = polydata.GetPoints()
    numPts = points.GetNumberOfPoints()
    print(f"Processing '{infile}': Total Points in input: {numPts}")

    # Get the "concentration" array and convert to NumPy array
    concArray = polydata.GetPointData().GetArray("concentration")
    if concArray is None:
        print(f"Error: 'concentration' array not found in {infile}!")
        return
    conc = numpy_support.vtk_to_numpy(concArray)  # shape (numPts,)

    # Convert the point coordinates to a NumPy array
    pts = numpy_support.vtk_to_numpy(points.GetData())  # shape (numPts, 3)

    # Filter: Remove points with concentration < 25
    mask = conc >= 25
    filtered_pts = pts[mask]
    filtered_conc = conc[mask]
    num_filtered = filtered_pts.shape[0]
    print(f"Points after filtering (concentration >= 25): {num_filtered}")

    if num_filtered == 0:
        print(f"No points remaining in {infile} after filtering. Skipping this file.")
        return

    # Create the feature matrix for DBSCAN using spatial coordinates and concentration (weighted)
    concentration_weight = 0.9  # Adjust as needed
    features = np.hstack([filtered_pts, (filtered_conc.reshape(-1, 1) * concentration_weight)])
    # features shape: (num_filtered, 4)

    # Configure DBSCAN parameters; adjust eps and min_samples based on data scale
    eps = 1.0         # neighborhood radius
    min_samples = 10  # minimum points to form a cluster

    db = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = db.fit_predict(features)
    unique_labels = np.unique(cluster_labels)
    print(f"Unique DBSCAN cluster labels in {infile}: {unique_labels}")

    # Create output polydata from the filtered points and attach arrays:
    arrays_dict = {
        "concentration": filtered_conc.astype(np.float32),
        "DBSCAN_Labels": cluster_labels.astype(np.float32)  # converting to float for visualization if needed
    }
    # Retrieve the velocity array (if present)
    velocityArray = polydata.GetPointData().GetArray("velocity")
    if velocityArray is not None:
        velocity = numpy_support.vtk_to_numpy(velocityArray)
    else:
        print("Warning: 'velocity' array not found. Continuing without velocity.")
        velocity = None

    if velocity is not None:
        # Optionally if we want to filter velocity along with  points
        arrays_dict["velocity"] = velocity[mask].astype(np.float32)

    output_polydata = create_polydata_from_points(filtered_pts, arrays_dict)

    # Write the output polydata to an output VTU file
    write_vtu(output_polydata, outfile)
    print(f"Output written to: {outfile}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_folder_dbscan.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Find all .vtu files in the input folder
    input_files = glob.glob(os.path.join(input_folder, "*.vtu"))
    if not input_files:
        print("No .vtu files found in the input folder.")
        sys.exit(1)

    for infile in input_files:
        # Extract the filename and create the output file path
        filename = os.path.basename(infile)
        outfile = os.path.join(output_folder, filename)
        process_file(infile, outfile)

if __name__ == "__main__":
    main()
