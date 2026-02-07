SELECT 
    COUNT(DISTINCT(variant_id)) 
FROM variant
WHERE
    assembly = 'GRCh37' AND 
    chro = 13 AND
    chro_start >= 1000000 AND 
    chro_stop <= 20000000;