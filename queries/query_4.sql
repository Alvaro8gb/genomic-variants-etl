SELECT 
    v.ref_allele, 
    v.alt_allele, 
    COUNT(DISTINCT(variant_id)) AS n_variants
FROM variant v
JOIN variant_phenotypes vp ON v.ventry_id = vp.ventry_id
WHERE 
    v.variant_type = 'Deletion'
    AND (
        (vp.phen_ns = 'Orphanet' AND vp.phen_id = '227535')
        OR (vp.phen_ns = 'MONDO' AND vp.phen_id = '0016419')
        OR (vp.phen_ns = 'OMIM' AND vp.phen_id = '114480')
        OR (vp.phen_ns = 'MedGen' AND vp.phen_id = '87542')
    ) 
GROUP BY v.ref_allele, v.alt_allele
ORDER BY n_variants DESC
LIMIT 1; 