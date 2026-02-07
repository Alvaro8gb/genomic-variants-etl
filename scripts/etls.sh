#!/bin/bash

DATA_PATH="data"
DUMP_PATH="dumps"

DATA_PATH_CLINVAR="$DATA_PATH/clinvar"
DATA_PATH_CIVIC="$DATA_PATH/civic"


DATE_CLINVAR="2025-12"
DATE_CIVIC="01-Dec-2025"

mkdir -p "$DUMP_PATH"

python clinvar_variant_etl.py \
    $DUMP_PATH/clinvar_variant.db \
    $DATA_PATH_CLINVAR/variant_summary_$DATE_CLINVAR.txt.gz

python clinvar_gene_stats_etl.py \
    $DUMP_PATH/clinvar_gene_stats.db \
    $DATA_PATH_CLINVAR/gene_specific_summary_$DATE_CLINVAR.txt.gz


python clinvar_submission_etl.py \
    $DUMP_PATH/clinvar_submission.db \
    $DATA_PATH_CLINVAR/submission_summary_$DATE_CLINVAR.txt.gz
 

python civic_variant_etl.py \
    $DUMP_PATH/civic_variant.db \
    $DATA_PATH_CIVIC/$DATE_CIVIC-VariantSummaries.tsv

