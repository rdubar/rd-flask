import os

from plexapi.server import PlexServer
import time, argparse, os
from dataclasses import dataclass
from tqdm import tqdm

from rog_tools import load_data, save_data, log, time_ago, show_file_size

# Plex Server Credentials
PLEX_IP = '192.168.0.238'
PLEX_PORT = '32400'
PLEX_TOKEN = os.environ.get('PLEX_TOKEN', None)
if not PLEX_TOKEN: log('NO PLEX TOKEN!')

PlEX_DATA = './plex.data'

@dataclass
class PlexRecord:
    plex: object

    def __post_init__(self):
        p = self.plex
        empty = None
        self.title = p.title
        self.year = p.year if hasattr(p,'year') else empty
        self.entry = get_entry(self.title, self.year)
        self.art = p.art if hasattr(p,'art') else empty
        self.thumb = p.thumb if hasattr(p,'thumb') else empty
        self.summary = p.summary if hasattr(p,'summary') else empty
        self.tagline = p.tagline if hasattr(p,'tagline') else empty
        self.duration = p.duration if hasattr(p,'duration') else empty
        self.added = p.addedAt if hasattr(p,'addedAt') else empty
        m = p.media[0] if hasattr(p,'media') else None
        self.codec = m.videoCodec if hasattr(m,'videoCodec') else empty
        self.bitrate = m.bitrate if hasattr(m,'bitrate') else empty
        self.height = m.height if hasattr(m,'height') else empty
        self.width = m.width if hasattr(m,'width') else empty
        f = m.parts[0] if hasattr(m,'parts') else empty
        self.size = f.size if hasattr(f, 'size') else empty
        self.file = f.file if hasattr(f, 'file') else empty

        year = f' ({self.year })' if self.year else ''
        quality = f' {self.height}' if self.height else ''
        self.plex = f'{self.title}{year}{quality}'

    def __str__(self):
        return self.plex


def plex_url(part):
    # http://192.168.0.244:32400{m.thumb()}?X-Plex-Token=dbufy5hZk2k91QpxYUuW')
    return f'http://{PLEX_IP}:{PLEX_PORT}{part}?X-Plex-Token={PLEX_TOKEN}'

def get_entry(title, year):
    entry = title.lower()
    if year:
        entry += f' ({year})'
    return entry

def connect_to_plex(    server_ip = PLEX_IP,
                        port = PLEX_PORT,
                        token = PLEX_TOKEN
                            ):
    # Connect to the Plex server
    if not PLEX_TOKEN:
        print('No Plex Token: unable to connect to Plex')
        return []
    baseurl = f'http://{server_ip}:{port}'
    print(f'Connecting to Plex server at {server_ip}. Please wait...')
    clock = time.perf_counter()
    try:
        plex = PlexServer(baseurl, token)
    except Exception as e:
        print('Failed to connect to Plex: {e}')
        return []
    clock = time.perf_counter() - clock
    print(f'Connected in {clock:.2f} seconds. Getting library, please wait...')
    clock = time.perf_counter()
    try:
        plex_media = plex.library.all()
    except Exception as e:
        print(f'Failed to get data from Plex: {e}')
        return []
    clock = time.perf_counter() - clock
    print(f'Received {len(plex_media):,} objects from Plex in {clock:.2f} seconds.')

    def process(token):
        return token['text']

    return plex_media


def update_media_records(update=False, reset = False, verbose=False):
    if reset:
        log('Resetting all media records...')
        records = []
    else:
        # load the current data
        records = load_data(PlEX_DATA) or []
    if not update and records:
        return records

    entries = [ x.entry for x in records ] if records else []
    # get the plex media objects
    plex_media = connect_to_plex()
    new = []
    for item in plex_media:
        year = item.year if hasattr(item,'year') else ''
        entry = get_entry(item.title, year)
        if not entry in entries:
            new.append(item)
    u = len(new)
    if u > 0:
        d = f'Updating plex info for {u} items'
        if verbose:
            for x in new:
                print(x.entry)
        for item in tqdm(new, desc=d):
            m =  PlexRecord(item)
            records.append(m)
        records = sorted(records, key=lambda x: (x.entry))
        save_data(PlEX_DATA, records)
    else:
        log('All records are up-to-date.')
    return records

def search_records(text, records):
    if not text or not records: return
    lower = text.lower()
    print(f'Searching for: {lower}')
    matches = 0
    for item in records:
        if lower in str(vars(item)).lower():
            print(item.entry)
            matches += 1
    print(f'{matches} matches for "{lower}".')

def show_latest(records, number=10, verbose=False, reverse=False):
    """ show the latest [n] records (or all if 'verbose') """
    reverse = not reverse # ensure default behaviouir is newest first
    items = [x for x in records if x.added != None]
    desc = 'newest' if reverse else 'oldest'
    latest = sorted(items, key=lambda x: (x.added), reverse=reverse)
    if verbose: number = len(records)
    print(f'Showing {desc} {number} records.')
    for i in range(number):
        print(latest[i])


def show_quality(records, number=10, verbose=False, reverse=False):
    """ show the lowest [n] resolution records (or all if 'verbose') """
    quality = 'highest' if reverse else 'lowest'
    height = [ x for x in records if x.height != None ]
    lowest = sorted(height, key=lambda x: (x.height) or 0, reverse=reverse)
    if verbose: number = len(records)
    print(f'Showing {number} {quality} resolution records.')
    for i in range(number):
        print(lowest[i])

def show_size(records, number=10, verbose=False, reverse=False):
    """ show the largest [n] resolution records (or all if 'verbose') """
    quality = 'largest' if reverse else 'smallest'
    size = [ x for x in records if x.size != None ]
    largest = sorted(size, key=lambda x: (x.size) or 0, reverse=reverse)
    if verbose: number = len(records)
    print(f'Showing {number} {quality} file size items.')
    for i in range(number):
        print(largest[i], show_file_size(largest[i].size))

def main():
    parser = argparse.ArgumentParser()
    p = parser.add_argument
    p("search", help="search the library", type=str, nargs='*')
    p("-q", '--quality', help="show [10] highest resolution items", type=int, nargs='?', const=10)
    p("-n", '--new', help="show [10] newest items", type=int, nargs='?', const=10)
    p("-s", '--size', help="show [10] smallest file size items", type=int, nargs='?', const=10)
    p("-r", "--reverse", help="reverse the order of any list", action="store_true")
    p("-u", "--update", help="update the library", action="store_true")
    p("-v", "--verbose", help="increase output verbosity", action="store_true")
    p("--reset", help="reset the library", action="store_true")
    args = parser.parse_args()
    verbose = args.verbose
    reverse = args.reverse

    if verbose: print(f'Verbose mode. Arguments: {args}')

    data = update_media_records(update=args.update, reset=args.reset, verbose=verbose)

    if args.quality:
        show_quality(data, number = args.quality, verbose=verbose, reverse=reverse)

    if args.size:
        show_size(data, number = args.size, verbose=verbose, reverse=reverse)

    if args.new:
        show_latest(data, number = args.new, verbose=verbose, reverse=reverse)

    if args.search:
        search = ' '.join(args.search).lower()
        search_records(search, data)

if __name__== "__main__" :
    main()