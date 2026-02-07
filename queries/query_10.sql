SELECT 
    assembly, 
    chro, 
    COUNT(DISTINCT(variant_id)) AS n_variants
FROM variant
WHERE chro IN ('1', '22', 'X') 
  AND (assembly = 'GRCh37' OR assembly = 'GRCh38')
GROUP BY assembly, chro;