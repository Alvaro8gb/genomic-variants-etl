SELECT 
    variant_id,
    gene_symbol,
    chro,
    chro_start,
    chro_stop 
FROM variant
WHERE 
    assembly = 'GRCh38' AND
    phenotype_list LIKE '%Acute infantile liver 
    failure due to synthesis defect of mtDNA-encoded proteins%';