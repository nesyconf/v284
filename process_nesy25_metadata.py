#!/usr/bin/env python3
"""
Process NeSy 2025 metadata and generate markdown output grouped by tracks.
"""

import json
import random
from collections import defaultdict
from typing import List, Dict, Any

def load_metadata(file_path: str) -> List[Dict[str, Any]]:
    """Load metadata from JSONL file."""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def split_entries(entries: List[Dict[str, Any]], num_partitions: int = 3) -> List[List[Dict[str, Any]]]:
    """Randomly split entries into partitions."""
    # Shuffle entries for random distribution
    shuffled_entries = entries.copy()
    random.shuffle(shuffled_entries)
    
    # Calculate partition sizes
    total_entries = len(shuffled_entries)
    base_size = total_entries // num_partitions
    remainder = total_entries % num_partitions
    
    partitions = []
    start_idx = 0
    
    for i in range(num_partitions):
        # Add one extra entry to early partitions if there's a remainder
        partition_size = base_size + (1 if i < remainder else 0)
        end_idx = start_idx + partition_size
        partitions.append(shuffled_entries[start_idx:end_idx])
        start_idx = end_idx
    
    return partitions

def group_by_track(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group entries by track."""
    grouped = defaultdict(list)
    for entry in entries:
        track = entry.get('submission_content', {}).get('track', 'Unknown Track')
        grouped[track].append(entry)
    return dict(grouped)

def generate_markdown(partition: List[Dict[str, Any]], partition_num: int) -> str:
    """Generate markdown output for a partition."""
    grouped_entries = group_by_track(partition)
    
    markdown = f"## Poster Session Day {partition_num}\n\n"
    
    # Sort tracks alphabetically for consistent output
    for track in ["Main Track", "Neurosymbolic Generative Models", "Knowledge Graphs, Ontologies and Neurosymbolic AI", "Neurosymbolic Methods for Trustworthy and Interpretable AI"]:
        markdown += f"**{track}**\n\n"
        
        for entry in grouped_entries[track]:
            submission = entry.get('submission_content', {})
            title = submission.get('title', 'No Title')
            authors = submission.get('authors', [])
            link = submission.get('link', '#')
            type = submission.get('paper_type', 'Unknown Type')
            
            # Format authors as italic text
            authors_text = ', '.join(authors) if authors else 'Unknown Authors'
            
            markdown += f"- {title} (_{authors_text}_). **{type}**, [OpenReview link]({link})\n"
        
        markdown += "\n"
    
    return markdown

def main():
    """Main function to process metadata and generate output."""
    # Set random seed for reproducible results
    random.seed(42)
    
    # Load metadata
    file_path = "nesy25/nesy25__metadata.jsonl"
    entries = load_metadata(file_path)
    
    print(f"Loaded {len(entries)} entries from {file_path}")
    
    # Split into partitions
    partitions = split_entries(entries, 3)
    
    print(f"Split into {len(partitions)} partitions:")
    for i, partition in enumerate(partitions, 1):
        print(f"  Partition {i}: {len(partition)} entries")
    
    # Generate markdown for each partition
    for i, partition in enumerate(partitions, 1):
        markdown = generate_markdown(partition, i)
        
        # Write to file
        output_file = f"partition_{i}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Generated {output_file}")
        
        # Also print to console
        print(f"\n{'='*50}")
        print(f"PARTITION {i}")
        print(f"{'='*50}")
        print(markdown)

if __name__ == "__main__":
    main()
