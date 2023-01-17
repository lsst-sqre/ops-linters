#!/bin/bash
# Run the linter

set -eu

source /etc/linters/secrets/slack
source /etc/linters/secrets/aws

/opt/venv/bin/python /opt/route53-checker/checker.py
