#!/usr/bin/env bash
# Executa os testes de ligação às bases de dados (tests/test_dbs.py).
# Uso: ./run_test_dbs.sh   ou   bash run_test_dbs.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR/src"
exec pytest tests/test_dbs.py -v "$@"
