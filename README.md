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
