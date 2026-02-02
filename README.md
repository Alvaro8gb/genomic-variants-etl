# Genomic Variants ETL

## Allele Registry

### Canonical Allele Identifier
e.g. CA251355
https://reg.clinicalgenome.org/


El **Canonical Allele Identifier (CAID)** es un identificador único, permanente y universal asignado a una variante genética específica.

Su función principal es servir como un **"ancla de identidad"** en bioinformática. En genética, una misma variante puede tener nombres distintos dependiendo de:

* La **versión del genoma** utilizada (ej. GRCh37 vs. GRCh38).
* La **secuencia de referencia** (si se mira el ADN genómico, el ARNm o la proteína).
* El **software** que la nombre.

El CAID conecta todas esas descripciones diferentes bajo un solo código "canónico" para asegurar que todos los científicos y bases de datos hablen de lo mismo.

¿Para qué sirve?

* **Interoperabilidad:** Permite que diferentes bases de datos (como ClinVar, gnomAD y dbSNP) intercambien información sin errores.
* **Permanencia:** Si la versión del genoma humano se actualiza, el nombre HGVS puede cambiar, pero el CAID permanece igual.
* **Claridad clínica:** Evita que un laboratorio clasifique una variante como "benigna" y otro como "patogénica" simplemente porque la están llamando de forma distinta.



## Clinvar


### Qué significa `gene_id = -1` ?

> Indica que la variante **no está asignada de forma inequívoca a un gen específico.**

- Variante intergénica: Está entre genes, no dentro de uno conocido.

- Región reguladora o no codificante: Por ejemplo: upstream/downstream, intrones profundos, regiones promotoras sin asignación clara.
- Variante estructural o grande
- Deleciones/duplicaciones que abarcan varios genes o regiones amplias
- Información incompleta o ambigua en ClinVar



### Qué significa `position_vcf = -1` y `ref_allele = na`

> indica que **no puede representarse como una variante genómica estándar en formato VCF**.

Esto ocurre porque:

* ClinVar **no puede asignar una posición genómica única**
* No es una **SNV ni un indel simple**
* No se puede definir **REF/ALT**

Suele pasar con:

* Variantes descritas solo a nivel **proteico o cDNA**
* Variantes **estructurales o complejas**
* Grandes deleciones/duplicaciones o descripciones antiguas


## Queries

### 1. ¿Cuántas variantes están relacionadas con el gen P53 tomando como referencia el ensamblaje GRCh38 en ClinVar y en CIViC?


```sql

SELECT 
    COUNT(DISTINCT variant_id)
FROM variant
WHERE 
    gene_symbol IN ('TP53', 
    'P53', 'BCC7', 'LFS1', 
    'BMFS5', 'TRP53')  -- https://www.ncbi.nlm.nih.gov/gene/7157
    AND assembly = 'GRCh38';

```

CLinvar: 3,758
Civic: 0

### 2. ¿Qué cambio del tipo “single nucleotide variant” es más frecuente, el de una Guanina por una Adenina, o el una Guanina por una Timina? Usad las anotaciones basadas en el ensamblaje GRCh37 para cuantificar y proporcionar los números totales, tanto para ClinVar como para CIViC.


```sql

SELECT 
    ref_allele,
    alt_allele,
    COUNT(variant_id) AS n_variants
FROM variant
WHERE 
    assembly = 'GRCh37' 
    -- AND variant_type = 'single nucleotide variant' 
    AND (
        (ref_allele = 'G' AND alt_allele = 'A') OR
        (ref_allele = 'G' AND alt_allele = 'T')
    )
GROUP BY ref_allele, alt_allele
ORDER BY n_variants DESC;


```
CLinvar:
|ref_allele|alt_allele|n_variants|
|----------|----------|----------|
|G|A|798290|
|G|T|232695|

Civic:

|ref_allele|alt_allele|n_variants|
|----------|----------|----------|
|G|A|105|
|G|T|54|


### 3. ¿Cuáles son los tres genes de ClinVar con un mayor número de inserciones, deleciones o indels? Usa el ensamblaje GRCh37 para cuantificar y proporcionar los números totales.

```sql

SELECT 
	gene_symbol,
	COUNT(DISTINCT(variant_id)) as n_variants
FROM variant
WHERE assembly = 'GRCh37' AND 
	variant_type IN (
      'Indel',
      'Insertion',
      'Deletion'
      )
GROUP BY gene_symbol
ORDER BY n_variants DESC
LIMIT 3;
```

|gene_symbol|n_variants|
|-----------|----------|
|BRCA2|3788|
|BRCA1|3034|
|NF1|2954|


### 4. ¿Cuál es la deleción más común en el cáncer hereditario de mama en CIViC? ¿Y en ClinVar? Por favor, incluye en la respuesta además en qué genoma de referencia, el número de veces que ocurre, el alelo de referencia y el observado.

https://www.ebi.ac.uk/ols4/ontologies/mondo

'hereditary breast carcinoma': https://www.ebi.ac.uk/ols4/ontologies/mondo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FMONDO_0016419

```sql

SELECT 
    v.ref_allele, 
    v.alt_allele, 
    COUNT(DISTINCT(variant_id)) AS n_variants
FROM variant v
JOIN variant_phenotypes p ON v.ventry_id = p.ventry_id
WHERE 
    v.variant_type = 'Deletion' AND
    v.assembly = 'GRCh37' AND 
    p.phen_id = '0016419' AND p.phen_ns = 'MONDO'
GROUP BY v.ref_allele, v.alt_allele
ORDER BY n_variants DESC
LIMIT 1; 
```

|ref_allele|alt_allele|n_variants|
|----------|----------|----------|
|CT|C|355|


### 5. Ver el identificador de gen y las coordenadas de las variantes de ClinVar del ensamblaje GRCh38 relacionadas con el fenotipo del Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins.

```sql
SELECT 
	variant_id,
	gene_symbol,
	chro,
	chro_start,
	chro_stop,
	phenotype_list 
FROM variant
WHERE 
	assembly = 'GRCh37' AND
	phenotype_list LIKE '%Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins%';
```


|variant_id|gene_symbol|chro|chro_start|chro_stop|phenotype_list|
|----------|-----------|----|----------|---------|--------------|
|1290|TRMU|22|46731689|46731689|Deafness, mitochondrial, modifier of&#124;not specified&#124;Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins&#124;not provided&#124;Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins;Aminoglycoside-induced deafness|
|1291|TRMU|22|46733822|46733822|Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins&#124;not provided&#124;Aminoglycoside-induced deafness&#124;TRMU-related disorder|
|1293|TRMU|22|46749706|46749706|Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins|
|1294|TRMU|22|46731663|46731663|Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins|
|30819|TRMU|22|46749726|46749726|Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins&#124;not provided&#124;Inborn genetic diseases&#124;Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins;Aminoglycoside-induced deafness&#124;Aminoglycoside-induced deafness|
|137708|TRMU|22|46742350|46742350|not provided&#124;not specified&#124;Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins&#124;Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins;Aminoglycoside-induced deafness|

### 6. Para aquellas variantes de ClinVar con significancia clínica “Pathogenic” o “Likely pathogenic”, recuperar las coordenadas, el alelo de referencia y el alelo alterado para la hemoglobina (HBB) en el assembly GRCh37.

```sql
SELECT 
	v.variant_id,
	v.chro,
	v.chro_start,
	v.chro_stop
FROM variant v
JOIN clinical_sig c ON v.ventry_id = c.ventry_id
WHERE
	c.significance IN ('Pathogenic', 'Likely pathogenic') AND
	v.assembly = 'GRCh37' AND
	v.gene_symbol ='HBB';
```

|variant_id|significance|gene_symbol|chro|chro_start|chro_stop|
|----------|------------|-----------|----|----------|---------|
|15090|Pathogenic|HBB|11|5246841|5246841|
|15090|Likely pathogenic|HBB|11|5246841|5246841|
|15096|Pathogenic|HBB|11|5246837|5246837|
|15112|Pathogenic|HBB|11|5246836|5246836|
|15122|Pathogenic|HBB|11|5247865|5247865|
|15126|Pathogenic|HBB|11|5248233|5248233|


### 7. Calcular el número de variantes del ensamblaje GRCh37 que se encuentren en el cromosoma 13, entre las coordenadas 10,000,000 y 20,000,000 , tanto para ClinVar como para CIViC.

```sql

SELECT 
	COUNT(DISTINCT(variant_id)) 
FROM variant
WHERE
	assembly = 'GRCh37' AND 
	chro = 13 AND
	chro_start >= 1000000 AND 
	chro_stop <= 20000000;
```

Clinvar: 70
Civic: 0



### 8. Calcular el número de variantes de ClinVar para los cuáles se haya provisto entradas de significancia clínica que no sean inciertas (“Uncertain significance”), del ensamblaje GRCh38, en aquellas variantes relacionadas con BRCA2.

```sql

SELECT 
	COUNT(DISTINCT(v.variant_id))
FROM variant v
JOIN clinical_sig c ON v.ventry_id = c.ventry_id
WHERE
	c.significance = 'Uncertain significance' AND
	v.assembly = 'GRCh38' AND
	v.gene_symbol ='BRCA2';

```

Clinvar: 16733



### 9. Obtener el listado de pubmed_ids de ClinVar relacionados con las variantes del ensamblaje GRCh38 relacionadas con el fenotipo del glioblastoma.

```sql

ATTACH DATABASE 'clinvar_submission.db' as subs;


SELECT 
    v.ventry_id,
    v.variant_id ,
    s.submission_id,
    p.pmid, 
    v.phenotype_list
FROM variant v
JOIN subs.clinvar_submission s 
    ON v.variant_id = s.variant_id 
 JOIN subs.variant_pmid p
    ON s.submission_id = p.submission_id 
WHERE 
	v.assembly = 'GRCh38' AND 
	v.phenotype_list LIKE '%glioblastoma%'; 
LIMIT 10;


```

```sql

SELECT 
    p.pmid
FROM (
    SELECT * FROM variant 
    WHERE assembly = 'GRCh38' AND 
    phenotype_list LIKE '%glioblastoma%'
    LIMIT 1000
) v
JOIN subs.clinvar_submission s ON v.variant_id = s.variant_id 
JOIN subs.variant_pmid p ON s.submission_id = p.submission_id
```


|pmid|
|----|
|20522432|
|27666373|
|29979965|
|32000721|
|11370630|
|24122735|


### 10. Obtener el número de variantes del cromosoma 1 y calcular la frecuencia de mutaciones de este cromosoma, tanto para GRCh37 como para GRCh38. ¿Es esta frecuencia mayor que la del cromosoma 22? ¿Y si lo comparamos con el cromosoma X? 

Tomad para los cálculos los tamaños cromosómicos disponibles tanto en https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh37.p13 como en https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38.p13 . 
Para esta pregunta se debe usar solo los datos proporcionados por ClinVar.

| Cromosoma | Longitud GRCh37 (bp) | Longitud GRCh38 (bp) |
|----------|----------------------|----------------------|
| 1        | 249,250,621          | 248,956,422          |
| 22       | 51,304,566           | 50,818,468           |
| X        | 155,270,560          | 156,040,895          |


Dado que frecuencia de mutaciones es 

$$\text{Frecuencia} = \frac{\text{Número de Variantes}}{\text{Tamaño del Cromosoma (bp)}}$$


Same query for both

```sql
SELECT 
    assembly, 
    chro, 
    COUNT(DISTINCT(variant_id)) AS n_variants
FROM variant
WHERE chro IN ('1', '22', 'X') 
  AND (assembly = 'GRCh37' OR assembly = 'GRCh38')
GROUP BY assembly, chro;
```

#### Clinvar

```bash
python freq_variants.py dumps/clinvar_variant.db 

```

Variants per chro and assembly

| assembly   | chro   |   n_variants |
|:-----------|:-------|-------------:|
| GRCh37     | 1      |       376941 |
| GRCh37     | 22     |        91898 |
| GRCh37     | X      |       186235 |
| GRCh38     | 1      |       373143 |
| GRCh38     | 22     |        90386 |
| GRCh38     | X      |       181254 |

Frequency of mutations

| Chromosome   |   Variants_GRCh37 |   Frequency_GRCh37 |   Variants_GRCh38 |   Frequency_GRCh38 |
|:-------------|------------------:|-------------------:|------------------:|-------------------:|
| 1            |            376941 |         0.0015123  |            373143 |         0.00149883 |
| 22           |             91898 |         0.00179122 |             90386 |         0.00177861 |
| X            |            186235 |         0.00119942 |            181254 |         0.00116158 |

### Civic

```bash
python freq_variants.py dumps/civiv_variant.db
```

Variants per chro and assembly

| assembly   | chro   |   n_variants |
|:-----------|:-------|-------------:|
| GRCh37     | 1      |           58 |
| GRCh37     | 22     |           14 |
| GRCh37     | X      |           22 |
| GRCh38     | 1      |            1 |

Frequency of mutations

| Chromosome   |   Variants_GRCh37 |   Frequency_GRCh37 |   Variants_GRCh38 |   Frequency_GRCh38 |
|:-------------|------------------:|-------------------:|------------------:|-------------------:|
| 1            |                58 |        2.32698e-07 |                 1 |        4.01677e-09 |
| 22           |                14 |        2.7288e-07  |               nan |      nan           |
| X            |                22 |        1.41688e-07 |               nan |      nan           |
