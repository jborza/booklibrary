import subprocess

def get_metadata(filepath):
    """
    Extract author and title metadata from an ebook file using Calibre's ebook-meta CLI.
    Supports EPUB, MOBI, AZW3, PDB, and more.
    Requires Calibre installed and 'ebook-meta' in your PATH.
    Returns (author, title).
    """
    try:
        result = subprocess.run(
            ["ebook-meta", filepath],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        lines = result.stdout.splitlines()
        title = author = None
        for line in lines:
            if line.startswith("Title"):
                title = line.split(":", 1)[1].strip()
            elif line.startswith("Author(s)"):
                author = line.split(":", 1)[1].strip()
        #sometimes author includes author name in [ ] brackets, we can remove it
        if author and '[' in author:
            author = author.split('[')[0].strip()
        return author, title
    except Exception as e:
        print(f"Failed to extract metadata for {filepath}: {e}")
        return None, None