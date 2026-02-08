bash scripts/download.sh
bash scripts/etls.sh

python querie_caller.py \
    --ddbb clinvar \
    dumps/clinvar_variant.db \
    dumps/clinvar_gene_stats.db \
    dumps/clinvar_submission.db \
    --ddbb civic \
    dumps/civic_variant.db \
    dumps/civic_clinical.db \
    dumps/civic_molecular.db
