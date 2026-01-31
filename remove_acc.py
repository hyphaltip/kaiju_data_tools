#!/usr/bin/env python3
"""
Remove sequences from a FASTA file based on accession numbers.

This script reads a FASTA file and a list of accession numbers to remove,
then outputs a filtered FASTA file without the specified sequences.
"""

import argparse
import sys


def read_accessions_to_remove(accession_file):
    """
    Read accession numbers from a file.
    
    Args:
        accession_file: Path to file containing accession numbers (one per line)
                       Lines starting with '#' are treated as comments and ignored.
    
    Returns:
        set: Set of accession numbers to remove
    """
    accessions = set()
    with open(accession_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                accessions.add(line)
    return accessions


def process_fasta(input_fasta, output_fasta, accessions_to_remove):
    """
    Process FASTA file and remove sequences with specified accession numbers.
    
    Args:
        input_fasta: Path to input FASTA file
        output_fasta: Path to output FASTA file (or sys.stdout)
        accessions_to_remove: Set of accession numbers to filter out
    """
    removed_count = 0
    kept_count = 0
    current_header = None
    current_sequence = []
    skip_current = False
    
    def write_sequence(header, sequence, out_file):
        """Write a FASTA sequence to the output file."""
        out_file.write(header + '\n')
        out_file.write(''.join(sequence) + '\n')
    
    # Determine output file
    if output_fasta == '-' or output_fasta is None:
        out_file = sys.stdout
    else:
        out_file = open(output_fasta, 'w')
    
    try:
        with open(input_fasta, 'r') as in_file:
            for line in in_file:
                line = line.rstrip('\n\r')
                
                if line.startswith('>'):
                    # Process previous sequence if exists
                    if current_header is not None:
                        if not skip_current:
                            write_sequence(current_header, current_sequence, out_file)
                            kept_count += 1
                        else:
                            removed_count += 1
                    
                    # Start new sequence
                    current_header = line
                    current_sequence = []
                    
                    # Check if this accession should be removed
                    # Extract accession from header (first word after '>')
                    parts = line.split()
                    accession = parts[0][1:] if len(parts) > 0 and len(parts[0]) > 1 else ''
                    skip_current = accession in accessions_to_remove
                    
                elif current_header is not None:
                    # Append sequence line
                    current_sequence.append(line)
            
            # Process last sequence
            if current_header is not None:
                if not skip_current:
                    write_sequence(current_header, current_sequence, out_file)
                    kept_count += 1
                else:
                    removed_count += 1
    
    finally:
        if out_file != sys.stdout:
            out_file.close()
    
    # Print statistics to stderr
    print(f"Kept {kept_count} sequences, removed {removed_count} sequences", 
          file=sys.stderr)


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description='Remove sequences from a FASTA file based on accession numbers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.fasta accessions.txt -o output.fasta
  %(prog)s input.fasta accessions.txt > output.fasta
  
The accession file should contain one accession number per line.
Accessions are matched against the first word in the FASTA header (after '>').
        """
    )
    
    parser.add_argument(
        'fasta_file',
        help='Input FASTA file'
    )
    
    parser.add_argument(
        'accession_file',
        help='Text file with accession numbers to remove (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='-',
        help='Output FASTA file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Read accessions to remove
    accessions_to_remove = read_accessions_to_remove(args.accession_file)
    print(f"Loaded {len(accessions_to_remove)} accession(s) to remove", 
          file=sys.stderr)
    
    # Process FASTA file
    process_fasta(args.fasta_file, args.output, accessions_to_remove)


if __name__ == '__main__':
    main()
