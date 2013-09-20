fotoworkflow
============

Composite image(*) handling library
--------------------------------

- Automate the identification and generation of composite images of a series of photos
such as HDR, panorama images using EXIF data.
- Automate parts of the HDR and panorama creation workflow.

(*) Composite image: an image that is created using several (occasionally several 100s)
of images.

Prerequisites
-------------

Python modules beyond a usual python installation: pyexiv2, hsi (Hugin Scripting interface)

Tools
- align_image_stack
- enfuse
- enblend
- dcraw

Installation
------------
TBD


Documentation
-------------

This library helps with the workflow of handling images created using more than one photo taken. I call them composite image as the final output is composed of several images such as HDR or panorama images
 by automating the identification and parts of the generation steps.

The following image sequences are supported
- HDR
- Panorama
- Focus stacks
- Time lapse

