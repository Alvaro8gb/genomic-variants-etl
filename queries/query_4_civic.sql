SELECT 
    v.ref_allele, 
    v.alt_allele,
    v.variant_types,
    COUNT(DISTINCT(v.variant_id)) AS n_variants
FROM ( 
    SELECT
        DISTINCT pv.variant_id 
	FROM clinical_evidence ce
	JOIN disease d 
		ON d.doid = ce.doid
	JOIN profile_variant pv 
		ON pv.molecular_profile_id = ce.molecular_profile_id 
    WHERE 
        d.disease_name LIKE "%breast cancer%" AND
        ce.evidence_type = "Predisposing"
) v_c
JOIN variant v ON v.variant_id = v_c.variant_id
GROUP BY v.ref_allele, v.alt_allele, v.variant_types 
ORDER BY n_variants DESC