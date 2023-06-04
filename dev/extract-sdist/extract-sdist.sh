#! /usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${SCRIPT_PATH%journal-manager*}journal-manager"

OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"

pushd "${PROJET_PATH}" > /dev/null

source .venv/bin/activate

DIST_FOLDER="${OUTPUT_FOLDER}/dist"
mkdir -p "${DIST_FOLDER}"

EXTRACT_FOLDER="${OUTPUT_FOLDER}/extract"
mkdir -p "${EXTRACT_FOLDER}"

pyproject-build --outdir "${DIST_FOLDER}" .


tar -xf "${DIST_FOLDER}/journal-manager-0.0.2.tar.gz" -C "${EXTRACT_FOLDER}"

popd > /dev/null
