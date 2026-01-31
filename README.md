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

```bash
./kaiju_nr_prepare.py \
  -i kaiju-taxonlistEuk.tsv \
  -d /srv/projects/db/ncbi/preformatted/20260128/swissprot \
  -o /scratch/euk_nr
```

This will create:
- `/scratch/euk_nr.txt` - intermediate output from blastdbcmd
- `/scratch/euk_nr.faa` - final FASTA file with converted newlines

#### Options

- `-i, --input`: Input TSV file with taxon IDs in first column (required)
- `-d, --database`: Path to BLAST database (required)
- `-o, --output`: Output directory or file prefix (required)
- `--dbtype`: Database type (default: prot)
- `--outfmt`: Output format string (default: `>%a_%T %t\n%s`)
- `--no-target-only`: Do not use -target_only flag

#### Requirements

- Python 3.6+
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

## Installation

This tool uses only Python 3 standard library, so no additional dependencies are required.

**Requirements:**
- Python 3.6 or higher

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
