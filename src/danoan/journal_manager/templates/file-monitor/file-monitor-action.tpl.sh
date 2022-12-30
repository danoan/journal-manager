#! /usr/bin/env bash

SCRIPT_PATH="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"

mkdir -p "${OUTPUT_FOLDER}"

TEMP_BUILD_FOLDER="${OUTPUT_FOLDER}/build"
rm -rf "${TEMP_BUILD_FOLDER}"
mkdir -p "${TEMP_BUILD_FOLDER}"

MODIFIED_FILE="$1"
JOURNALS_FILES_FOLDER="{{data.journals_files_folder}}"
JOURNALS_SITE_FOLDER="{{data.journals_site_folder}}"

MODIFIED_FILE_PREFIX_REMOVED="${MODIFIED_FILE#${JOURNALS_FILES_FOLDER}/}"
JOURNAL_FOLDER_NAME="${MODIFIED_FILE_PREFIX_REMOVED%%/*}"

if [ -n ${JOURNAL_FOLDER_NAME} ]
then

    JOURNAL_LOCATION_FOLDER="${JOURNALS_FILES_FOLDER}/${JOURNAL_FOLDER_NAME}"
    echo "Rebuilding: ${JOURNAL_LOCATION_FOLDER}" 
    
    journal-manager b --ignore-safety-questions --do-not-build-index --build-location "${TEMP_BUILD_FOLDER}" --jl "${JOURNAL_LOCATION_FOLDER}"
    
    rm -rf "${JOURNALS_SITE_FOLDER}/${JOURNAL_FOLDER_NAME}"
    mv -f "${TEMP_BUILD_FOLDER}/site/${JOURNAL_FOLDER_NAME}" "${JOURNALS_SITE_FOLDER}"

fi


