#!/bin/sh

rm env.py pre.sh Containerfile
ln -s ./platforms/vsphere/env.py
ln -s ./platforms/vsphere/pre.sh
ln -s ./platforms/vsphere/Containerfile