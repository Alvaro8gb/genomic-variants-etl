import pandas as pd

class Query:
    """Base class for SQL queries"""
    MAX_ROWS = 10
    
    def execute(self, cursor, query: str):
        """Execute a given query method and return results"""
        try:
            print(f"Executing query: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            
            print(pd.DataFrame(results[:self.MAX_ROWS], 
                               columns=columns).to_markdown(index=False))
            
            if len(results) > 10:
                print(f"... 10 results of {len(results)}")
        except Exception as e:
            print(f"Error executing query: {e}")
    
    def read_query_from_file(self, file_path) -> str:
        """Read SQL query from a file and return it as a string"""
        try:
            with open(file_path, 'r') as file:
                query = file.read()
            return query
        except Exception as e:
            print(f"Error reading query from file: {e}")
            return ""

    def query_1(self, cursor, conn):
        """
        ¿Cuántas variantes están relacionadas con el gen P53 tomando como referencia el
        ensamblaje GRCh38 en ClinVar y en CIViC?
        """
        query = self.read_query_from_file("queries/query_1.sql")
        self.execute(cursor, query)
    
    def query_2(self, cursor, conn):
        """
        ¿Qué cambio del tipo “single nucleotide variant” es más frecuente, el de una Guanina por
        una Adenina, o el una Guanina por una Timina? Usad las anotaciones basadas en el
        ensamblaje GRCh37 para cuantificar y proporcionar los números totales, tanto para
        ClinVar como para CIViC.
        """
        query = self.read_query_from_file("queries/query_2.sql")
        self.execute(cursor, query)
    
    def query_3(self, cursor, conn):
        """
        ¿Cuáles son los tres genes de ClinVar con un mayor número de inserciones, deleciones
        o indels? Usa el ensamblaje GRCh37 para cuantificar y proporcionar los números totales.
        """
        query = self.read_query_from_file("queries/query_3.sql")
        self.execute(cursor, query)

    
    def query_5(self, cursor, conn):
        """
        Ver el identificador de gen y las coordenadas de las variantes de ClinVar del ensamblaje
        GRCh38 relacionadas con el fenotipo del Acute infantile liver failure due to synthesis
        defect of mtDNA-encoded proteins.
        """
        query = self.read_query_from_file("queries/query_5.sql")
        self.execute(cursor, query)
    
    def query_6(self, cursor, conn):
        """
        Para aquellas variantes de ClinVar con significancia clínica “Pathogenic” o “Likely
        pathogenic”, recuperar las coordenadas, el alelo de referencia y el alelo alterado para la
        hemoglobina (HBB) en el assembly GRCh37.
        """
        query = self.read_query_from_file("queries/query_6.sql")
        self.execute(cursor, query)
    
    def query_7(self, cursor, conn):
        """
        Calcular el número de variantes del ensamblaje GRCh37 que se encuentren en el
        cromosoma 13, entre las coordenadas 10,000,000 y 20,000,000 , tanto para ClinVar como
        para CIViC.
        """
        query = self.read_query_from_file("queries/query_7.sql")
        self.execute(cursor, query)
    
    def query_8(self, cursor, conn):
        """
        Calcular el número de variantes de ClinVar para los cuáles se haya provisto entradas de
        significancia clínica que no sean inciertas (“Uncertain significance”), del ensamblaje
        GRCh38, en aquellas variantes relacionadas con BRCA2.
        """
        query = self.read_query_from_file("queries/query_8.sql")
        self.execute(cursor, query)
    
    def query_9(self, cursor, conn):
        """
        Obtener el listado de pubmed_ids de ClinVar relacionados con las variantes del
        ensamblaje GRCh38 relacionadas con el fenotipo del glioblastoma.
        """
        query = self.read_query_from_file("queries/query_9.sql")
        self.execute(cursor, query)
    
    def query_10(self, cursor, conn):
        """
        Obtener el número de variantes del cromosoma 1 y calcular la frecuencia de mutaciones
        de este cromosoma, tanto para GRCh37 como para GRCh38. ¿Es esta frecuencia mayor
        que la del cromosoma 22? ¿Y si lo comparamos con el cromosoma X? Tomad para los
        cálculos los tamaños cromosómicos disponibles tanto en
        https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh37.p13 como en
        https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38.p13 . Para esta pregunta se
        debe usar solo los datos proporcionados por ClinVar.
        """
        CHR_DATA_BP = {
            'chro': ['1', '22', 'X'],
            'length_GRCh37': [249_250_621, 51_304_566, 1552_70_560],
            'length_GRCh38': [248_956_422, 50_818_468, 156_040_895]
        }

        query = self.read_query_from_file("queries/query_10.sql")
        df_lengths = pd.DataFrame(CHR_DATA_BP)

        print("Chromosome length by assembly")
        print(df_lengths.to_markdown(index=False))

        df_freq_variantes = pd.read_sql_query(query, conn)
        print("Variants per chro and assembly")
        print(df_freq_variantes.to_markdown(index=False))

        df_freq_with_lengths = df_freq_variantes.merge(df_lengths, on='chro')
        
        # Calculate mutation frequency (mutations per bp)
        df_freq_with_lengths['freq_GRCh37'] = df_freq_with_lengths.apply(
            lambda row: row['n_variants'] / row['length_GRCh37'] if row['assembly'] == 'GRCh37' else None, axis=1
        )

        df_freq_with_lengths['freq_GRCh38'] = df_freq_with_lengths.apply(
            lambda row: row['n_variants'] / row['length_GRCh38'] if row['assembly'] == 'GRCh38' else None, axis=1
        )

        df_freq_pivot = df_freq_with_lengths.pivot(
            index='chro',
            columns='assembly',
            values=['n_variants', 'freq_GRCh37', 'freq_GRCh38']
        )

        # Flatten the multi-level columns
        df_freq_pivot.columns = ['_'.join(col).strip()
                                for col in df_freq_pivot.columns.values]

        # Rename columns for clarity
        df_freq_pivot = df_freq_pivot.rename(columns={
            'n_variants_GRCh37': 'Variants_GRCh37',
            'n_variants_GRCh38': 'Variants_GRCh38',
            'freq_GRCh37_GRCh37': 'Frequency_GRCh37',
            'freq_GRCh38_GRCh38': 'Frequency_GRCh38'
        })

        # Select only the relevant columns and reset index
        df_freq_pivot = df_freq_pivot[[
            'Variants_GRCh37', 'Frequency_GRCh37', 'Variants_GRCh38', 'Frequency_GRCh38']].reset_index()
        df_freq_pivot.rename(columns={'chro': 'Chromosome'}, inplace=True)

        print("Frequency of mutations")

        print(df_freq_pivot.to_markdown(index=False))

class ClinvarQuery(Query):
    """ClinVar specific queries"""
    def query_4(self, cursor, conn):
        """
        ¿Cuál es la deleción más común en el cáncer hereditario de mama en CIViC? ¿Y en
        ClinVar? Por favor, incluye en la respuesta además en qué genoma de referencia, el
        número de veces que ocurre, el alelo de referencia y el observado.
        """
        query = self.read_query_from_file("queries/query_4_clinvar.sql")
        self.execute(cursor, query)


class CivicQuery(Query):
    """CiVic specific queries"""
    def query_4(self, cursor, conn):
        """
        ¿Cuál es la deleción más común en el cáncer hereditario de mama en CIViC? ¿Y en
        ClinVar? Por favor, incluye en la respuesta además en qué genoma de referencia, el
        número de veces que ocurre, el alelo de referencia y el observado.
        """
        query = self.read_query_from_file("queries/query_4_civic.sql")
        self.execute(cursor, query)