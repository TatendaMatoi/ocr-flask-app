#!/usr/bin/env bash

apt-get update && \
apt-get install -y tesseract-ocr poppler-utils && \
echo "Tesseract installed!"
