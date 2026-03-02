#!/usr/bin/env python3
"""
Subset fonts based on HTML content using pyftsubset.
Extracts all text from HTML and creates optimized font subsets.
"""

import os
import sys
from pathlib import Path
from html.parser import HTMLParser
import subprocess


class TextExtractor(HTMLParser):
    """Extract text content from HTML, skipping script and style tags."""
    
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip = True
    
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = False
    
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)


def extract_text_from_html(html_file):
    """Extract all text content from an HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = TextExtractor()
    parser.feed(content)
    return parser.get_text()


def extract_text_from_astro(astro_file):
    """Extract text from an Astro file by parsing the template portion."""
    with open(astro_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content += content.upper()
    return content


def get_unique_characters(text):
    """Get all unique characters from text."""
    return ''.join(sorted(set(text)))


def subset_font(font_path, output_path, text):
    """Subset a font file using pyftsubset."""
    try:
        cmd = [
            'pyftsubset',
            font_path,
            f'--text={text}',
            f'--output-file={output_path}',
            '--flavor=woff2'
        ]
        
        print(f"Subsetting: {Path(font_path).name}")
        print(f"  Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Created: {Path(output_path).name}")
            original_size = os.path.getsize(font_path)
            subset_size = os.path.getsize(output_path)
            reduction = (1 - subset_size / original_size) * 100
            print(f"  Size: {original_size:,} → {subset_size:,} bytes ({reduction:.1f}% reduction)")
        else:
            print(f"  ✗ Error: {result.stderr}")
            return False
        
        return True
    
    except FileNotFoundError:
        print("Error: pyftsubset not found. Install with: pip install fonttools")
        return False


def main():
    # Configuration
    html_files = [
        'src/pages/index.astro',
        'src/components/Sticker.astro',
    ]
    
    # Additional glyphs to always include
    additional_glyphs = '👻👹🤡⛈⚡👾←→'
    
    font_files = [
        {
            'name': 'ABCStefan Simple',
            'input': 'public/ABCStefan-Simple.woff2',
            'output': 'public/ABCStefan-Simple.subset.woff2'
        },
        {
            'name': 'ABCStefan Bubble',
            'input': 'public/ABCStefan-Bubble.woff2',
            'output': 'public/ABCStefan-Bubble.subset.woff2'
        },
        {
            'name': 'ABCGravityVariable',
            'input': 'public/ABCGravityVariable.woff2',
            'output': 'public/ABCGravityVariable.subset.woff2'
        }
    ]
    
    # Extract text from all HTML/Astro files
    print("📄 Extracting text from HTML/Astro files...")
    all_text = ""
    
    for html_file in html_files:
        if not os.path.exists(html_file):
            print(f"  ⚠ Skipping missing file: {html_file}")
            continue
        
        print(f"  Reading: {html_file}")
        if html_file.endswith('.astro'):
            text = extract_text_from_astro(html_file)
        else:
            text = extract_text_from_html(html_file)
        
        all_text += text
    
    # Add additional glyphs
    all_text += additional_glyphs
    
    # Get unique characters
    unique_chars = get_unique_characters(all_text)
    print(f"\n📊 Found {len(unique_chars)} unique characters")
    print(f"   Characters: {repr(unique_chars[:100])}")
    if len(unique_chars) > 100:
        print(f"   ... and {len(unique_chars) - 100} more")
    
    # Subset each font
    print(f"\n🔤 Subsetting fonts...")
    success_count = 0
    
    for font in font_files:
        if not os.path.exists(font['input']):
            print(f"  ⚠ Skipping missing font: {font['input']}")
            continue
        
        if subset_font(font['input'], font['output'], unique_chars):
            success_count += 1
    
    print(f"\n✅ Subsetting complete! {success_count}/{len(font_files)} fonts processed")
    
    if success_count > 0:
        print("\n💡 Update your HTML to use the subset fonts:")
        print("   Replace @font-face urls with the .subset.woff2 versions")


if __name__ == '__main__':
    main()
