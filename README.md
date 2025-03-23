# CS(5/6)040 Final Project: Visualizing the Saffman-Taylor Instability

# Deliverables

- Effective Visualizations of the Saffman-Taylor Instability facilitated by the IEEE SciVis 2016 contest dataset
- Interactive controls to manipulate the visualization to show different properties of the dataset/different facets of the Saffman-Taylor Instability
- A portable program which can be used assuming the required dataset is supplied


# Dataset
The entire dataset (400+gb) can be obtained from [The San Diego Supercomputing Center](https://cloud.sdsc.edu/v1/AUTH_sciviscontest/2016/README.html). We also offer a subset of the dataset (5gb) available via [USU Box](https://usu.box.com/s/spgzms9nc8fen8mdbf9fnq5pt9hvzy10)

# Tasks

- [ ] Create a portable environment which can display the dataset on any system using **Trame**
    - [ ] Make paths to dataset dynamic so program can be run from any directory/system
    - [ ] Create graceful error handling for if something is missing or file permissions are set up incorrectly
    - [ ] This task will be complete once the dataset can be initialized and viewed from a web browser using Trame. Validation step would be having another groupmate try the completed environment
- [ ] Visualization Selection: Use paraview to find compelling visualizations of the dataset
    - [ ] Determine best parameters for the following visualizations
        - [ ] Path Lines
        - [ ] Steam Lines
        - [ ] Glyphs
        - [ ] Point clouds
        - [ ] Flow Volumes
        - [ ] Threshold sliders to only include particles that exceed a certain threshold for a certain property of the data (velocity and concentration)
        - [ ] Another part of this task will be finding appealing color maps and transfer functions to apply to these visualizations
        - [ ] this task will be complete once we have `.psvm` for each visualization allowing for reference/recreation of the obtained visualization/parameters
- [ ] Extend our Trame implementation to include these visualizations
    - [ ] Path Lines
    - [ ] Steam Lines
    - [ ] Glyphs
    - [ ] Point clouds
    - [ ] Flow Volumes
    - [ ] Threshold sliders to only include particles that exceed a certain threshold for a certain property of the data (velocity and concentration)
    - [ ] After that, we can add controls for these visualizations which allow for manipulations within the tolerances of the best found parameters
    - [ ] This task is complete once the Trame environment supports viewing & manipulating our desired visualizations
- [ ] Mid-project check in report
    - [ ] This task will be complete once we have submitted our check in report via canvas
- [ ] Author the final project report stating what we built and the research outcomes
    - [ ] This task will be complete once we have submitted our final report via canvas
- [ ] Implementation Demonstration
    - [ ] This task will be complete once we have a demo video showing the interactive visualization working submitted via canvas.

**These tasks are stretch goals if our current scope proves to be too small**
- [ ] Plots to describe the data: use plots provided by matplotlib (which is supported by trame) to further explain phenomena in the dataset (concentration distribution, particle movement amount, etc)
- [ ] Controls to change the run/resolution used in visualization
- [ ] Toggles to enable multiple visualizations simultaneously (perhaps only allow complementary visualizations; not just any arbitrary combination)

