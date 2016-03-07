#! /bin/sh

set -e

new="$(date -Iseconds)"
mkdir "$new"

if [ -e latest ]; then
    latest="$(readlink latest)"
fi

rsync --archive \
      --hard-links \
      --acls \
      --xattrs \
      --sparse \
      --one-file-system \
      --human-readable \
      --progress \
      ${latest:+--link-dest="$(pwd)/$latest"} \
      / "${1:-.}/${new}/"  \
      2>&1 \
  | xz -c9 \
  >> backup.log.xz

if [ -e latest ]; then
    rm latest
fi
ln -s "$new" latest
