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


## Civic 

### DOID 

https://www.ebi.ac.uk/ols4/ontologies/doid

El DOID (Disease Ontology ID) es el ID universal de una enfermedad.

- Función: Estandariza los nombres de los cánceres (ej. DOID:8552 para Leucemia Mieloide Crónica).
- Utilidad: Permite que tu base de datos sea compatible con otros sistemas hospitalarios y de investigación a nivel mundial.