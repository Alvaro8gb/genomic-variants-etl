SELECT 
    v.variant_id,
    c.significance,
    v.chro,
    v.chro_start,
    v.chro_stop
FROM variant v
JOIN clinical_sig c ON v.ventry_id = c.ventry_id
WHERE
    c.significance IN ('Pathogenic', 'Likely pathogenic') AND
    v.assembly = 'GRCh37' AND
    v.gene_symbol ='HBB';