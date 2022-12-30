#! /usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${SCRIPT_PATH%add-quick-note*}add-quick-note"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"


JOURNAL_NAME="${1}"
TEXT_NOTE="${2}"

JOURNAL_LOCATION_FOLDER="$(journal-manager journal show "${JOURNAL_NAME}" "location_folder")"
QUICK_NOTES_MARKDOWN="${JOURNAL_LOCATION_FOLDER}/docs/quick-notes.md"

if [[ ! -e "${QUICK_NOTES_MARKDOWN}" ]]
then
    touch "${QUICK_NOTES_MARKDOWN}"
fi

# There is a bug in the mktemp in the alpine image. The following
# does not work:
# mktemp -t -p output quicknotes.XXXXX.toml
QUICK_NOTES_TOML="$(mktemp -t -p"${OUTPUT_FOLDER}" )"
quick-notes generate-toml "${QUICK_NOTES_MARKDOWN}" > "${QUICK_NOTES_TOML}"
quick-notes generate-quick-note "${TEXT_NOTE}" >> "${QUICK_NOTES_TOML}"
quick-notes generate-markdown "${QUICK_NOTES_TOML}" > "${QUICK_NOTES_MARKDOWN}"

# This is necessary to trigger `entr`. Otherwise, the build job is not executed.
touch "${QUICK_NOTES_MARKDOWN}"
rm "${QUICK_NOTES_TOML}"
