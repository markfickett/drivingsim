#!/bin/bash
protoc drivingsim.proto --python_out=.
./main.py
