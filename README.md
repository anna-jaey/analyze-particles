# Analyze Particles ImageJ

This script runs particle analysis on nd2 files in one directory.

* open nd2 file with split channels
* for *TRITC* channel:
    * maximum intensity projection
    * AutoThreshold (Method: Default, "ignore black")
    * Watershed
    * analyze particles
* saves:
    * maximum intensity projection images with particle outlines
    * drawings of the outlines
    * results csv for every single image
    * at the end: summary csv for all images
