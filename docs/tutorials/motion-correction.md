During 2-photon calcium imaging, motion artifacts can pollute your raw recording and needs to corrected in order to enable analyses using ROIs (Regions Of Interest).

`drim2p` uses the [`SIMA`](https://github.com/losonczylab/sima) ([DOI](https://doi.org/10.3389/fninf.2014.00080)) library to carry out motion correction.

## Motion settings

Motion correction requires some additional information related to the strategy to use as well as the maximum expected displacement of pixels throughout the recording. This information is passed along to `drim2p` using a settings file. For this tutorial, we will use the default file available from the repository. Once you understand the workflow a bit better, you can customise it as described in the [how-to guide]().

In order to inform `drim2p` of which settings to use, you should download the [default settings file](https://github.com/DuguidLab/drim2p/blob/main/resources/motion_correction/settings.toml.base) and move it to the directory where your recording is.

You should then have the following file structure:

```shell
tutorial/
├── imaging_file.h5
├── imaging_file.ini
├── imaging_file.raw
├── imaging_file.xml
└── settings.toml.base  (NEW)
```

## Motion correcting

From there, motion correction is as easy as conversion. All you need to do if run the following command:

```shell
drim2p motion correct . --settings-path settings.toml.base
```

If all goes well, you will see some output along these lines:

```text
Applying motion correction for 'imaging_file' using DiscreteFourier2D.
Finished motion correction in 0h 1m 0.00s.
Saved motion correction to file.
```

The motion corrected data will be saved automatically. However, you won't see a new file in your directory. That is one of the strengths of HDF5. You can store multiple bits of information inside the same file. Think of it as a ZIP archive, it's essentially a folder structure but all inside of one file.

!!! note
    You don't need to keep the `settings.toml` file around your data. When you apply motion correction to a dataset, the settings used are added to the metadata of the motion corrected dataset.

## What's next?

After motion correction, you will now be able to select ROIs on your recording in order to then analyse their signals. `drim2p` provides a [GUI (Graphical User Interface) to draw ROIs on](roi-drawing.md).
