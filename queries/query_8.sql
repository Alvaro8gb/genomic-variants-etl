SELECT 
    COUNT(DISTINCT(v.variant_id))
FROM variant v
JOIN clinical_sig c ON v.ventry_id = c.ventry_id
WHERE
    c.significance != 'Uncertain significance' AND
    v.assembly = 'GRCh38' AND
    v.gene_symbol ='BRCA2';