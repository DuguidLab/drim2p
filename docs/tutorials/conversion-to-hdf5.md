The first step when working with RAW data is to convert it to a file format that allows shaping it correctly and appending metadata about its datatype, acquisition, etc. `drim2p` uses the [HDF5](https://en.wikipedia.org/wiki/Hierarchical_Data_Format) file format.

## Converting

With a terminal open in the directory with your files, simply run:

```shell
drim2p convert raw .
```

If all goes well, you will see some output along these lines:

```text
Converting 'imaging_file.raw'.
Finished converting 'imaging_file.raw'.
```

If you see a warning but no error, you file should still be converted properly, but some metadata might not be conserved.  

If you see an error, then something prevented the conversion from going ahead. The most common error looks like this:
```text
Failed to retrieve OME-XML metadata from INI file or directly through XML file. 
```

If you get this error, you should ensure you have the proper file structure as described in the [overview](index.md#prerequisites) then try again.

If you get a different error, you should read the message to try and understand what went wrong. If you are not sure how to solve it, try looking for the error message on the [issues page](https://github.com/DuguidLab/drim2p/issues?q=is%3Aissue).

## What's next?

At this point, you are finally ready to preprocess your data. The first step is to use [motion correction](motion-correction.md).
