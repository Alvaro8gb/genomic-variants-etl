SELECT 
    ref_allele,
    alt_allele,
    COUNT(variant_id) AS n_variants
FROM variant
WHERE 
    assembly = 'GRCh37' AND
    -- AND variant_type = 'single nucleotide variant' 
    ref_allele = 'G' 
    AND (alt_allele = 'A' OR alt_allele = 'T')
GROUP BY ref_allele, alt_allele
ORDER BY n_variants DESC;