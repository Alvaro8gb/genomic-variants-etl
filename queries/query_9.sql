SELECT 
    DISTINCT(sp.pmid)
FROM (
    SELECT DISTINCT(v.variant_id)
    FROM variant_phenotypes vp
    JOIN variant v ON v.ventry_id = vp.ventry_id
    WHERE
        v.assembly = 'GRCh38'
        AND (
            (vp.phen_ns = 'Orphanet' AND vp.phen_id = '360')
            OR (vp.phen_ns = 'MONDO' AND vp.phen_id = '0018177')
            OR (vp.phen_ns = 'OMIM' AND vp.phen_id = '137800')
            OR (vp.phen_ns = 'MedGen' AND vp.phen_id = '42228')
            OR (vp.phen_ns = 'MeSH' AND vp.phen_id = 'D005909')
        ) 
) v 
JOIN submission s ON v.variant_id = s.variant_id 
JOIN submission_pmid sp ON s.submission_id = sp.submission_id; 