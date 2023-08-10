# Introduction (Sample Mesher using Cubit)

The program is used to develop microstructural meshes with custom geometry, with the feature of exporting the crystallographic orientations of the individual grains. The following README was last updated on the 6th of June, 2023.

# Dependencies

The following section details the requirements to run the script.

## Cubit Coreform

Cubit Coreform is a great meshing toolbox. To use the script, you will need to install and get a license for Cubit Coreform.
* Install your desired version of Cubit Coreform from their [official website](https://coreform.com/products/downloads/).
* The educational license is free, but may have restricted functionalities, such as being able to export meshes with a limited number of elements.

The script also requires the user to give a path to the `psculpt.exe` file, which should come with the Cubit Coreform installation.
* The `psculpt.exe` file should be in the `bin` folder.
* To make the pathing easier, the user can create a symbolic link to the `bin` folder from the root directory.
* The command to create the symbolic link should have the following format.
```
$ ln -s <path/to/psculpt.exe> ~/
```
* An example of this command is shown below. In the example below, Cubit Coreform 2023.4 was installed for Windows, and the script is run from WSL 2.
```
$ ln -s '/mnt/c/Program Files/Coreform Cubit 2023.4/bin' ~/ 
```

## Python Packages

The scripts also require several Python packages. To install these packages, `pip` is required. If you do not have `pip` installed, please following [these instructions](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/).

* Numpy (`python3.9 -m pip install numpy`).
* PIL (`python3.9 -m pip install pillow`) for visualising and altering the sample's geometry.
* PyVista (`python3.9 -m pip install pyvista`) for extracting information from the exodus mesh files.


## Workflow

1. Initial pixellation of EBSD data
2. Remove voids and cleanup pixellation
3. Add homogenised material
4. Create sample shape using script
5. Manually reshape in MS Paint
6. Mesh
7. Identify bad quality elements in Cubit
8. Repeat steps 5, 6, and 7 until minimum quality is positive