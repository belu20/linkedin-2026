#!/bin/bash
xvfb-run --auto-servernum --server-num=0 --server-args="-screen 0 1024x800" python -u -W ignore api.py
