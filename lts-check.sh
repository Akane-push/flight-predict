#!/bin/sh

if grep -q "avx2" /proc/cpuinfo; then
    echo "DOCKERFILE=Dockerfile" >> .env
else
    echo "DOCKERFILE=Dockerfile.lts" >> .env
fi