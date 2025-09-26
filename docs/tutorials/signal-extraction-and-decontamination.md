`drim2p` uses [FISSA](https://github.com/rochefort-lab/fissa) ([DOI](https://doi.org/10.1038/s41598-018-21640-2)) for signal extraction and decontamination. Both of those steps are done in one command.

## Running the command

Like previous steps in this tutorial, extraction and decontamination only requires a single command:

```shell
drim2p extract signal .
```

If all goes well, you will see something along these lines:

```text
Extracting and decontaminating signal for 'imaging_file'.
Extracting traces: 100%|██████████████████| 1/1 [00:00<00:00, 3548.48it/s]
Finished extracting raw signals from 1 ROIs across 1 trials in 1 min, 0 sec.
Separating data: 100%|██████████████████| 1/1 [00:00<00:00, 41.16it/s]
Finished separating signals from 1 ROIs across 1 trials in 1 min, 0 sec
Finished extracting signal.
```

Once again, no extra file should be added to the directory, instead the extracted signals will be embedded into the HDF5 file.

!!! note
    FISSA outputs signal arrays in the shape (5, timepoints), where the first index is the "true" signal and the next four are the neuropil ones. `drim2p` only saves the "true" signal under the normal preprocessing group. However, the neuropil signals are still saved in the QA group.

## What's next?

The next step in the workflow is to [compute ΔF/F₀](dff-calculation.md) for the extracted signals.
