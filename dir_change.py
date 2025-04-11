
import sys

# Replaces instances of 'old_dir' with 'new_dir' in a .pvsm file.
def replace_directory_in_pvsm(pvsm_file, old_dir, new_dir):
    """
    Args:
        pvsm_file (str): Path to .pvsm file
        old_dir (str): Original directory name
        new_dir (str): Desired directory name

        EXAMPLE: python "isostate.psvm" "/home/chandler/Documents/cs6040-finalproj/run01-0.44/run" "/run01/run01/timestep"
    """
    try:
        with open(pvsm_file, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {pvsm_file}")
        return

    new_content = content.replace(old_dir, new_dir)

    try:
        with open(pvsm_file, 'w') as file:
            file.write(new_content)
        print(f"Success")
    except Exception as e:
        print(f"Error occurred while writing to: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python dir_change.py <pvsm_file> <old_dir> <new_dir>")
        sys.exit(1)

    pvsm_file = sys.argv[1]
    old_dir = sys.argv[2]
    new_dir = sys.argv[3]

    replace_directory_in_pvsm(pvsm_file, old_dir, new_dir)

