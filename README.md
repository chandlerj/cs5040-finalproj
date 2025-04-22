# CS(5/6)040 Final Project: Visualizing the Saffman-Taylor Instability

# Contributors
- Chandler Justice
- Ishara Mawelle 
- Emily LaBonty


# Deliverables

- Effective Visualizations of the Saffman-Taylor Instability facilitated by the IEEE SciVis 2016 contest dataset
- Interactive controls to manipulate the visualization to show different properties of the dataset/different facets of the Saffman-Taylor Instability
- A portable program which can be on any compatible system assuming the required dataset is supplied

# Dataset
The entire dataset (400+gb) can be obtained from [The San Diego Supercomputing Center](https://cloud.sdsc.edu/v1/AUTH_sciviscontest/2016/README.html). We also offer a subset of the dataset (5gb) available via [USU Box](https://usu.box.com/s/spgzms9nc8fen8mdbf9fnq5pt9hvzy10)

# Installation and setup

0. Download the Dataset from the USU Box mentioned above. Extract the desired run of the simulation into the `data/run01/` directory and bulk rename the `.vtu` files to the format `run_n.vtu`.

1. Set up conda envrionment with Trame and Paraview. The environment can be created and activated with the following commands
    ```
    conda create -n pv-env -c conda-forge paraview trame trame-vtk trame-vuetify
    conda activate pv-env
    ```
2. Perform the clustering algorithm to create the version of the dataset needed for clustering using the `DBSCAN` script

    `python utils/DBSCAN.py data/run01 data/run01_DBSCAN`

3. At this point, you should be ready to run the trame app.

    `python main.py`

# Other Visualizations and Demonstration Video

We also have some additional topological analysis of this dataset available in the `ms_[20, 30, 40, 50,59].pvsm` state files. These files can be loaded inside of paraview **after** loading the `TopologyToolKit` plugin within Paraview (Tools => Manage Plugins => Select `TopologyToolKit` => Press load selected). These give a topological breakdown using critical point analysis of the data at select time steps. 

Beyond this, we also have completed renderings and a demonstration video available on [Google Drive](https://drive.google.com/drive/folders/1I6ZTTRxMr5zN_VCXP5TDaXQaIwF4SmmD). Our demo video can be accessed directly [from here](https://drive.google.com/file/d/1TOYlnjXc1mQLMPYSBpkTsFqcUSFeT2C8/view?usp=sharing).

# Academic Integrity Notice

This repository contains a final project submission for Utah State University’s CS[5/6]040 course.

**Any attempt to use, copy, or submit material from this repository as your own work in any academic setting constitutes plagiarism and is a violation of academic integrity policies.** Such actions may result in severe disciplinary consequences, including academic penalties and a permanent mark on your academic record.

The authors of this project retain all rights to its contents and expressly disclaim any responsibility for academic misconduct by third parties who misuse this material.

**Do not copy or submit any content from this repository for academic credit**


