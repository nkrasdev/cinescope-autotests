#!/usr/bin/env bash

set -euo pipefail

missing_variables=()

for variable_name in "$@"; do
  if [[ -z "${!variable_name:-}" ]]; then
    missing_variables+=("$variable_name")
  fi
done

if (( ${#missing_variables[@]} > 0 )); then
  joined_variables=$(IFS=,; echo "${missing_variables[*]}")
  echo "::error::Missing required environment variables: ${joined_variables}"
  exit 1
fi
