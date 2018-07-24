#!/bin/bash

export JOURNAL_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ${JOURNAL_ROOT}/venv/bin/activate
PYTHONPATH=${PYTHONPATH}:${JOURNAL_ROOT}
python3 ${JOURNAL_ROOT}/app/microblog.py
