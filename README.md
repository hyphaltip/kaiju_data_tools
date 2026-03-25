# kaiju_data_tools
support for kaiju dataset prep

## Scripts

### kaiju_nr_prepare.py

A Python script for preparing non-redundant protein databases for Kaiju by extracting sequences from NCBI databases based on taxon IDs.

#### Usage

```bash
./kaiju_nr_prepare.py -i <taxon_list.tsv> -d <blast_db_path> -o <output_prefix>
```

#### Example
 Need to download and compress all of https://ftp.ncbi.nih.gov/blast/db/nr.* and https://ftp.ncbi.nih.gov/blast/db/taxdb.tar.gz
 Have `blastdbcmd` from NCBI BLAST in path.
```bash
./kaiju_nr_prepare.py \
  -i kaiju-taxonlistEuk.tsv \ # or path to this
  -d nr \ # Need to set BLASTDB variable or run in folder where taxdb and nr indexes are uncompressed 
  -o /scratch/euk_nr
```

This will create:
- `/scratch/euk_nr.faa` -  FASTA file with converted accessions_taxon

#### Options

- `-i, --input`: Input TSV file with taxon IDs in first column (required)
- `-d, --database`: Path to BLAST database (required)
- `-o, --output`: Output directory or file prefix (required)
- `--dbtype`: Database type (default: prot)
- `--outfmt`: Output format string (default: `>%a_%T %t\n%s`) # note have to pass in \n as a formatted char not the literal \n,
- `--no-target-only`: Do not use -target_only flag

#### Requirements

- Python 3.9+
- NCBI BLAST+ toolkit (blastdbcmd must be in PATH)
### remove_acc.py

Remove sequences from a FASTA file based on accession numbers.

**Usage:**
```bash
python3 remove_acc.py <fasta_file> <accession_file> [-o output_file]
```

**Arguments:**
- `fasta_file`: Input FASTA file
- `accession_file`: Text file containing accession numbers to remove (one per line)
- `-o, --output`: Output FASTA file (optional, defaults to stdout)

**Examples:**
```bash
# Output to a file
python3 remove_acc.py input.fasta accessions.txt -o output.fasta

# Output to stdout
python3 remove_acc.py input.fasta accessions.txt > output.fasta

# Pipe to another command
python3 remove_acc.py input.fasta accessions.txt | gzip > output.fasta.gz
```

**Accession File Format:**
```
# This is a comment - lines starting with # are ignored
NP_001234567.1
NP_444555666.1
NP_987654321.2
```

The script matches accessions against the first word in the FASTA header (the text immediately after the `>` character). Empty lines and lines starting with `#` are ignored.

### filter_fasta.py

Filter a FASTA file, excluding sequences based on species or description patterns in the header. Headers are expected in the format `>ID description [species]`.

By default, excludes sequences from `[Homo sapiens]` and those with `immunoglobulin heavy chain` or `immunoglobulin light chain` in the description.

**Usage:**
```bash
# From stdin/stdout
./filter_fasta.py < input.fasta > output.fasta

# With file arguments
./filter_fasta.py --input input.fasta --output output.fasta
```

**Options:**
- `--input`: Input FASTA file (default: stdin)
- `--output`: Output FASTA file (default: stdout)
- `--exclude-species SPECIES`: Exclude sequences containing this species string (case-sensitive, e.g. `[Homo sapiens]`). Can be specified multiple times.
- `--exclude-description PATTERN`: Exclude sequences whose header contains this string (case-insensitive). Can be specified multiple times.
- `--no-defaults`: Do not apply default exclusion patterns; only use patterns specified on the command line.

**Examples:**
```bash
# Use defaults (exclude Homo sapiens and immunoglobulin heavy/light chain)
./filter_fasta.py < input.fasta > output.fasta

# Add an extra species exclusion on top of defaults
./filter_fasta.py --exclude-species "[Mus musculus]" < input.fasta > output.fasta

# Replace defaults entirely with custom patterns
./filter_fasta.py --no-defaults \
    --exclude-species "[Homo sapiens]" \
    --exclude-description "hypothetical protein" \
    < input.fasta > output.fasta

# Multiple patterns
./filter_fasta.py \
    --exclude-species "[Mus musculus]" \
    --exclude-description "immunoglobulin kappa chain" \
    < input.fasta > output.fasta
```

## Installation

This tool uses only Python 3 standard library, so no additional dependencies are required.

**Requirements:**
- Python 3.9 or higher

**Setup:**
```bash
git clone https://github.com/hyphaltip/kaiju_data_tools.git
cd kaiju_data_tools
chmod +x remove_acc.py
```

## Testing

Sample test data is provided in the `test_data/` directory:

```bash
python3 remove_acc.py test_data/sample.fasta test_data/accessions_to_remove.txt -o test_output.fasta
```
