SELECT
    COUNT(DISTINCT variant_id)
FROM variant
WHERE
    gene_symbol IN ('TP53',
    'P53', 'BCC7', 'LFS1',
    'BMFS5', 'TRP53') -- https://www.ncbi.nlm.nih.gov/gene/7157
    AND assembly = 'GRCh38';