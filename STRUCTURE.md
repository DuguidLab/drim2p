# The Structure & Implementation of drim2p

This guide describes the high-level structure of `drim2p`, including the different preprocessing steps, module conventions and command-line interface, as prescribed by the `drim2p` governing body (mostly Michelle).

## Processing steps

### 1. Recording conversion to HDF5

Irrespective of which format data was acquired in, they should first be converted to HDF5.

There are a few reasons for this, but primarily it's to keep things consistent across the application and ease compatibility with the [NWB format](https://nwb-overview.readthedocs.io/en/latest/).


### 2. _(Optional)_ Session definition


### 3. Motion correction


### 4. Signal decontamination


### 5. ROI drawing


### 6. Signal extraction


### 7. ∆F/F calculation


### 8. _(Optional)_ Spike inference


### 9. _(Optional)_ Session stitching


### 10. _(Optional)_ NWB export


## Utilities


## Quality control 


## Data format


## CLI structure


## Module structure
