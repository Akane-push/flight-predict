#!/bin/sh

if grep -q "avx2" /proc/cpuinfo; then
    echo "\nDOCKERFILE=Dockerfile" >> .env
else
    echo "\nDOCKERFILE=Dockerfile.lts" >> .env
fi