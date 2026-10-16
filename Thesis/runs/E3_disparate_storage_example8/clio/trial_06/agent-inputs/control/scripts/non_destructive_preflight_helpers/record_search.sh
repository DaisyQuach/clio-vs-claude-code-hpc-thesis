#!/usr/bin/env bash
# Usage: record_search.sh <collection_alias> <path> <method> <purpose>
# Appends one line to provenance/sources_searched.tsv. Records only; touches nothing else.
source "$(dirname "$0")/_common.sh"
[[ $# -eq 4 ]] || die "usage: record_search.sh <collection_alias> <path> <method> <purpose>"
append_tsv "$TRIAL_ROOT/provenance/sources_searched.tsv" $'utc\tcollection_alias\tpath\tmethod\tpurpose' "$(utc)" "$1" "$2" "$3" "$4"
