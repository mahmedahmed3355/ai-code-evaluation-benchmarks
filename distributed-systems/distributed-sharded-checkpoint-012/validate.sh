#!/bin/sh
set -eu
rm -rf /tmp/checkpoints
python -m app.validate /tmp/checkpoints
