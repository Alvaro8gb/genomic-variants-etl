SELECT 
    gene_symbol,
    COUNT(DISTINCT(variant_id)) as n_variants
FROM variant
WHERE 
    assembly = 'GRCh37' AND     
    variant_type IN ('Indel', 'Insertion', 'Deletion')
GROUP BY gene_symbol
ORDER BY n_variants DESC
LIMIT 3;