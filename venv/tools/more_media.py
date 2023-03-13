from dataclasses import dataclass
import os

@dataclass
class MediaRecord:

    title: str
    source: str
    quality: str
    extras: bool = False

    def __str__(self):
        return self.title

def get_movie_list():
    path = '/Users/roger/p/movie_list.txt'
    if not os.path.exists(path):
        print(f'Movie List Path not found: {path}')
        return []
    with open(path, 'r') as f:
        lines = f.read().splitlines()
    records = []
    for entry in lines:
        parts = entry.split()
        if len(parts) < 3:
            continue
        if parts[-1].lower() == 'extras':
            extras = True
            parts = parts[:-1]
        else:
            extras = False
        quality = parts[-1]
        source = parts[-2]
        title = ' '.join(parts[:-2])
        m = MediaRecord(title=title, source=source, quality=quality, extras=extras)
        records.append(m)
    if len(records) == 0:
        print(f'No media records found in {path}')
    return records

def main():
    records = get_movie_list()
    print(f'Media records: {len(records)} items found.')

if __name__== "__main__" :
    main()