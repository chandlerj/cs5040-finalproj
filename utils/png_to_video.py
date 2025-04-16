import cv2
import os
import glob
import sys
import argparse

###### Vibe coded ########
def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert PNG images to an MP4 video.")
    parser.add_argument("folder", type=str,
                        help="Path to the folder containing PNG files named like run.0000.png, run.0001.png, etc.")
    parser.add_argument("--fps", type=int, default=30,
                        help="Frames per second for the output video (default: 30)")
    args = parser.parse_args()

    folder = args.folder
    # Define the pattern to find files. Adjust the extension if your files are different.
    pattern = os.path.join(folder, "run.*.png")
    file_list = sorted(glob.glob(pattern))
    if not file_list:
        print(f"No files found in the folder '{folder}' matching the pattern run.*.png")
        sys.exit(1)

    # Read the first image to get the frame dimensions
    first_frame = cv2.imread(file_list[0])
    if first_frame is None:
        print(f"Could not read the image file: {file_list[0]}")
        sys.exit(1)
    height, width, layers = first_frame.shape

    # Set up the VideoWriter
    # The 'mp4v' codec is used here.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_filename = os.path.join(folder, "output.mp4")
    video_writer = cv2.VideoWriter(output_filename, fourcc, args.fps, (width, height))

    for filename in file_list:
        frame = cv2.imread(filename)
        if frame is None:
            print(f"Warning: Skipping file {filename} (could not read)")
            continue
        video_writer.write(frame)

    # Release the VideoWriter
    video_writer.release()
    print(f"Video successfully saved as {output_filename}")


if __name__ == "__main__":
    main()
