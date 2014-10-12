#!/bin/bash

for file in *.jpg ; do
    convert "$file" -font Bookman-Demi \
        -pointsize 72 -fill white -annotate +100+100 \
        %[exif:DateTimeOriginal] "new-${file}"
done
