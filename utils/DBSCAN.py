#!/usr/bin/env python
import sys, os, glob
import vtk
import numpy as np
from vtk.util import numpy_support
from sklearn.cluster import DBSCAN

# ---------------------------
# Global variable for tracked labels
global_next_label = 0
# To store centroids of clusters from the previous time frame,
# mapping global label -> centroid (as numpy array of shape (3,))
last_frame_centroids = {}

# Parameters for tracking matching
# Maximum allowed centroid distance to match clusters between frames
MATCH_DISTANCE_THRESHOLD = 3.0  # adjust as needed


def load_vtu(filename):
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


def write_vtu(data, filename):
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def create_polydata_from_points(points_array, arrays_dict=None):
    numPts = points_array.shape[0]
    vtk_pts = vtk.vtkPoints()
    vtk_pts.SetNumberOfPoints(numPts)
    for i in range(numPts):
        vtk_pts.SetPoint(i, points_array[i])
    ug = vtk.vtkUnstructuredGrid()
    ug.SetPoints(vtk_pts)
    for i in range(numPts):
        cell = vtk.vtkVertex()
        cell.GetPointIds().SetId(0, i)
        ug.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
    if arrays_dict is not None:
        for name, arr in arrays_dict.items():
            vtk_arr = numpy_support.numpy_to_vtk(num_array=arr, deep=True, array_type=vtk.VTK_FLOAT)
            vtk_arr.SetName(name)
            ug.GetPointData().AddArray(vtk_arr)
        if "Tracked_Labels" in arrays_dict:
            ug.GetPointData().SetActiveScalars("Tracked_Labels")
        elif "DBSCAN_Labels" in arrays_dict:
            ug.GetPointData().SetActiveScalars("DBSCAN_Labels")
    return ug


def assign_tracked_labels(filtered_pts, filtered_conc, cluster_labels):
    """
    Given filtered points, concentrations, and local DBSCAN cluster labels,
    compute centroids for each cluster and match them to clusters in the previous frame.
    Return a new array of tracked (global) labels.
    """
    global global_next_label, last_frame_centroids

    unique_local_labels = np.unique(cluster_labels)
    tracked_labels = np.full_like(cluster_labels, -1, dtype=np.int32)
    current_centroids = {}

    for lab in unique_local_labels:
        if lab < 0:
            # Noise stays as -1
            tracked_labels[cluster_labels == lab] = -1
            continue
        # Compute centroid for cluster with local label lab
        mask_lab = (cluster_labels == lab)
        pts_lab = filtered_pts[mask_lab]  # shape (n_lab, 3)
        centroid = np.mean(pts_lab, axis=0)
        current_centroids[lab] = centroid

        # If this is the very first frame (last_frame_centroids empty),
        # assign a new global label.
        if not last_frame_centroids:
            tracked_labels[mask_lab] = global_next_label
            # Store the centroid for this global label
            last_frame_centroids[global_next_label] = centroid
            global_next_label += 1
        else:
            # Try to match this cluster to one from the previous frame.
            assigned = False
            best_match_label = None
            best_match_dist = np.inf
            for glabel, prev_centroid in last_frame_centroids.items():
                dist = np.linalg.norm(centroid - prev_centroid)
                if dist < MATCH_DISTANCE_THRESHOLD and dist < best_match_dist:
                    best_match_label = glabel
                    best_match_dist = dist
            if best_match_label is not None:
                tracked_labels[mask_lab] = best_match_label
            else:
                tracked_labels[mask_lab] = global_next_label
                last_frame_centroids[global_next_label] = centroid
                global_next_label += 1
    # Update last_frame_centroids for next frame.
    # For simplicity, here we replace the entire mapping by current frame's global labels.
    # One might instead merge over time to increase robustness.
    new_last = {}
    # Recompute new_last mapping: for each unique tracked label in the current frame, compute centroid over the cluster.
    unique_tracked = np.unique(tracked_labels)
    for gl in unique_tracked:
        if gl < 0:
            continue
        mask_global = (tracked_labels == gl)
        centroid_global = np.mean(filtered_pts[mask_global], axis=0)
        new_last[gl] = centroid_global
    last_frame_centroids = new_last

    return tracked_labels


def process_file(infile, outfile):
    print(f"Processing '{infile}'")
    polydata = load_vtu(infile)
    points = polydata.GetPoints()
    numPts = points.GetNumberOfPoints()
    print(f"  Total points: {numPts}")

    pts = numpy_support.vtk_to_numpy(points.GetData())
    concArray = polydata.GetPointData().GetArray("concentration")
    if concArray is None:
        print(f"Error: 'concentration' not found in {infile}!")
        return
    conc = numpy_support.vtk_to_numpy(concArray)

    # Filter: keep only points with concentration >= 25
    mask = conc >= 25
    filtered_pts = pts[mask]
    filtered_conc = conc[mask]
    num_filtered = filtered_pts.shape[0]
    print(f"  Points after filtering: {num_filtered}")
    if num_filtered == 0:
        print("  No points remaining; skipping file.")
        return

    # Feature matrix: use spatial coordinates and weighted concentration.
    concentration_weight = 0.8  # adjust as needed
    features = np.hstack([filtered_pts, (filtered_conc.reshape(-1, 1) * concentration_weight)])

    # DBSCAN clustering on the features
    eps = 0.8  # adjust neighborhood radius as needed
    min_samples = 10  # adjust min_samples
    db = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = db.fit_predict(features)
    unique_labels = np.unique(cluster_labels)
    print(f"  DBSCAN labels: {unique_labels}")

    # Compute tracked (global) labels that relate clusters across frames.
    tracked_labels = assign_tracked_labels(filtered_pts, filtered_conc, cluster_labels)

    # Optionally compute cluster mean concentration per point
    cluster_mean = np.zeros_like(tracked_labels, dtype=np.float32)
    for gl in np.unique(tracked_labels):
        if gl < 0:
            cluster_mean[tracked_labels == gl] = 0.0
        else:
            msk = tracked_labels == gl
            cluster_mean[msk] = np.mean(filtered_conc[msk])

    # Build output arrays dictionary
    arrays_dict = {
        "concentration": filtered_conc.astype(np.float32),
        "DBSCAN_Labels": cluster_labels.astype(np.float32),
        "Tracked_Labels": tracked_labels.astype(np.float32),
        "Cluster_Mean_Concentration": cluster_mean
    }
    velocityArray = polydata.GetPointData().GetArray("velocity")
    if velocityArray is not None:
        velocity = numpy_support.vtk_to_numpy(velocityArray)
        arrays_dict["velocity"] = velocity[mask].astype(np.float32)
    else:
        print("  Warning: 'velocity' not found.")

    output_polydata = create_polydata_from_points(filtered_pts, arrays_dict)
    write_vtu(output_polydata, outfile)
    print(f"  Output written to: {outfile}\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: python process_folder_dbscan_tracking.py <input_folder> <output_folder>")
        sys.exit(1)
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    os.makedirs(output_folder, exist_ok=True)
    input_files = sorted(glob.glob(os.path.join(input_folder, "*.vtu")))
    if not input_files:
        print("No VTU files found in input folder.")
        sys.exit(1)
    for infile in input_files:
        filename = os.path.basename(infile)
        outfile = os.path.join(output_folder, filename)
        process_file(infile, outfile)


if __name__ == "__main__":
    main()
