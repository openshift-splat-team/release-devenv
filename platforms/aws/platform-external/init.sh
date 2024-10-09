#!/bin/sh

rm env.py pre.sh Containerfile
ln -s ./platforms/aws/external/env.py
ln -s ./platforms/aws/external/pre.sh
ln -s ./platforms/aws/external/Containerfile