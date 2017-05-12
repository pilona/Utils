#! /bin/sh

# Script to take an old.pdf and a new.pdf, render them page-by-page, and then
# compose them in such a way as to highlight the differences between the two.
# Assumes:
# - both PDFs are the same length.
# - both PDFs have roughly the same content (i.e., haven't shifted all the
#   content by even a single pixel, unless you want to see a mess difference).
# - you're not trying to compare most images (if any) in any meaningful way
# I'll admit I don't even know if p4merge does a good job of PDF comparison, if
# at all.

set -e

# High enough DPI to compare them at not too little a resolution.
# Should be enough for 4K.
DPI=300
left="${1%.pdf}"
right="${2%.pdf}"
# Use an uncompressed bitmap because it's faster to read and write all of that
# from tmpfs than to compress and read and write.
# Don't use if memory-starved and where /tmp is tmpfs, not disk.
RASTER=pam
COLORSPACE=rgba
# Set to 0 to effectively omit context due to nondeterministic output caused by
# antialiasing (gives grayish outline artifacts on $left/$right rasterization).
# Set to [1-8] to control the antialising depth (mutool draw -A parameter).
# TODO: Underlay one, the other, or both of the originals, grayed out,
#       or do a three-way diff.
ANTIALIAS=0

tmpdir="$(mktemp --directory /tmp/pdfdiff.XXXXXX)"
# Render both PDFs as single, page-per-file PNGs.
# Don't antialias because the text raster is no longer deterministic.
mutool draw -o "${tmpdir}/${left}%03d.${RASTER}"  -A 0 -r $DPI ${COLORSPACE:+-c "$COLORSPACE"} "$1"
mutool draw -o "${tmpdir}/${right}%03d.${RASTER}" -A 0 -r $DPI ${COLORSPACE:+-c "$COLORSPACE"} "$2"


# For each rendered PNG
for old in "${tmpdir}/${left}"*.${RASTER}; do
    basename="${old#${tmpdir}/${left}}"
    new="${right}${basename}"
    composite="composite${basename}"

    # Skip identical pages
    cmp -s "${old}" "${tmpdir}/${new}" && continue

    # XOR the old and new (left/right) PDFs together
    echo "composite $composite"
    gm composite -compose Xor \
                 "${tmpdir}/${new}" \
                 "${old}" \
                 pam:- \
      | gm convert -background white \
                   -flatten pam:- "${tmpdir}/${composite}"
    # Fill in a white background above.
    # Should we do this? Might this wash out some things we don't want it to?
done

echo 'adjoin composite.pdf'
# Combine into one PDF.
# TODO: Not lose page numbering information?
gm convert -adjoin "${tmpdir}"/composite*.${RASTER} composite.pdf

# Remove intermediate rasters.
rm -rf "$tmpdir"
