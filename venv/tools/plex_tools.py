import os

from plexapi.server import PlexServer
import time, argparse, os, re, sys
from dataclasses import dataclass
from tqdm import tqdm

from rog_tools import load_data, save_data, log, time_ago, show_file_size, get_modified_time, showtime, read_env

# Plex Server Credentials
read_env('.plex')
"""
# Expects a .plex file in the same folder as plex_tools module with the following format:

PLEX_IP = '192.168.0.238'
PLEX_PORT = '32400'
PLEX_TOKEN = '?????????????'
"""

PLEX_DATA = './plex.data'


def object_clean(object, remove):
    """ Hack to clean object information for easy plain text search """
    text = str(object)
    text = re.sub('[^A-Za-z0-9 ]+', ' ', text).replace(remove,'')
    return text

def search_data(object):
    """ return lower case values of object vars for easy search """
    return str(vars(object).values()).lower()

@dataclass
class PlexRecord:
    """ Record to store desired information from a Plex object as text """
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
        self.directors = object_clean(p.directors,'Director') if hasattr(p, 'directors') else empty
        self.roles = object_clean(p.roles,'Role') if hasattr(p, 'roles') else empty
        self.writers = object_clean(p.writers,'Writer') if hasattr(p, 'writers') else empty
        m = p.media[0] if hasattr(p,'media') else None
        self.codec = m.videoCodec if hasattr(m,'videoCodec') else empty
        self.bitrate = m.bitrate if hasattr(m,'bitrate') else empty
        self.height = m.height if hasattr(m,'height') else empty
        self.width = m.width if hasattr(m,'width') else empty
        f = m.parts[0] if hasattr(m,'parts') else empty
        self.size = f.size if hasattr(f, 'size') else empty
        self.file = f.file if hasattr(f, 'file') else empty
        self.uncompressed = True if self.codec=='mpeg2video' else False

        year = f' ({self.year })' if self.year else ''
        quality = f' {self.height}' if self.height else ''
        uncompressed = f'***' if self.uncompressed else ''
        self.plex = f'{self.title}{year}{quality}{uncompressed}'

    def __str__(self):
        return self.entry.title()

    def display(self, bit=True):
        height = self.height if self.height else ''
        uncompressed = '*' if self.uncompressed else ''
        quality = f'{uncompressed}{height}'
        size = show_file_size(self.size)
        title = self.entry.title()
        bitrate = self.bitrate if bit and self.bitrate else ''
        codec = self.codec if self.codec else ''
        if codec == 'mpeg2video': codec = "*mpeg2"
        return f'{size:>8}{quality:>7}{bitrate:>7}{codec:>8}    {title}'



def plex_url(part):
    """ Build a plex URL """
    # http://192.168.0.244:32400{m.thumb()}?X-Plex-Token=dbufy5hZk2k91QpxYUuW')
    return f'http://{PLEX_IP}:{PLEX_PORT}{part}?X-Plex-Token={PLEX_TOKEN}'

def get_entry(title, year):
    """ Create an entry for media object in standard format: title (year) """
    entry = title.lower()
    if year:
        entry += f' ({year})'
    return entry

def connect_to_plex(    server_ip = None,
                        port = None,
                        token = None
                            ):
    global ENV
    if not server_ip:server_ip = os.environ.get('PLEX_IP')
    if not port: port = os.environ.get('PLEX_PORT')
    if not token: token = os.environ.get('PLEX_TOKEN')

    """Connect to the Plex server and return a list of Plex Objects """
    if not (token and port and server_ip):
        print(f'Plex server info missing: {server_ip}:{port}?{token}. Unable to connect.')
        return []
    baseurl = f'http://{server_ip}:{port}'
    print(f'Connecting to Plex server at {server_ip}:{port}. Please wait...')
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

    #def process(token):
    #    return token['text']

    return plex_media


def update_media_records(update=False, reset = False, verbose=False, maxtime=24, path=PLEX_DATA, debug=False):
    """ Update media records from the Plex Server Objects as required """
    # load the current data
    records = load_data(path) or []
    if reset:
        log('Resetting all media records...')
        records = []
    if not update and records:
        if ((time.time() - get_modified_time(path)) / 3600 > maxtime):
            print(f'Last update > {maxtime} hours ago. Updating automatically...')
        else:
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
        d = f'Updating plex info for {u:,} items'
        if verbose:
            for x in new:
                print(x)
        for item in tqdm(new, desc=d):
            if debug:
                print(vars(item))
                debug = False
            m =  PlexRecord(item)
            records.append(m)
        records = sorted(records, key=lambda x: (x.entry))
        save_data(path, records)
    else:
        log('All records are up-to-date.')
    return records

def search_records(text, records, verbose=False, quiet=False):
    """ Show result of search of media records """
    if not text or not records: return
    lower = text.lower()
    print(f'Searching for: {lower}')
    matches = []
    for item in records:
        if lower in search_data(item):
            print(item.display())
            if verbose: print(vars(item))
            matches.append(item)
    if not quiet: print(f'{len(matches)} matches for "{lower}".')
    return matches

def show_uncompressed(records, verbose=False, min=20):
    """ show uncompressed media records """
    uncompressed = [ x for x in records if x.uncompressed ]
    u  = len(uncompressed)
    r = len(records)
    percent = round(u / r * 100)
    output = f'Found {u} uncompressed mpeg in {r:,} total records ({percent}%).'
    print(output)
    if verbose:
        print(*uncompressed, sep='\n')
        if u > min: print(output)

def sort_by(records, attrib='size', reverse=False, verbose=False, quiet=False):
    """ function to sort media objects by a given attribute """
    r = len(records)
    filtered = [ x for x in records if hasattr(x, attrib) and getattr(x,attrib) != None ]
    if not quiet and len(filtered)==0:
        print(f"Filtered {r:,} records by '{attrib}, returned no items.")
        filtered = records
    elif verbose:
        print(f"Sorting {len(filtered):,} of {r:,} total records by '{attrib}.")
    sorted_list = sorted(filtered, key=lambda x: getattr(x,attrib), reverse=reverse)
    return sorted_list

def show_records(records, number=10, verbose=False, reverse=False, quiet=False, desc='description'):
    """ display [number] of records """
    r = len(records)
    if number > r: number = r
    reversed = ' (reversed)' if reverse else ''
    report = f"Showing {number:,} of {r:,} items sorted by '{desc}'{reversed}."
    if not quiet: print(report)
    for i in range(number):
        print(records[i].display())
    if verbose: print(report)


def main():
    clock = time.perf_counter()

    parser = argparse.ArgumentParser()
    p = parser.add_argument
    p("search", help="search the library", type=str, nargs='*')
    p("-n", '--number', help="show [10] items", type=int, nargs='?', const=10)
    p("-a", '--all', help="show all", action="store_true")
    p("-d", '--date', help="soft by date added", action="store_true")
    p("-p", '--pixels', help="soft by video height in pixels", action="store_true")
    p("-s", '--size', help="soft by file size", action="store_true")
    p("-r", "--reverse", help="reverse the order of any list", action="store_true")
    p("-m", "--mpeg", help="filter by uncompressed mpeg videos", action="store_true")
    p("-u", "--update", help="update the library", action="store_true")
    p("-q", '--quiet', help="quiet mode", action="store_true")
    p("-v", "--verbose", help="increase output verbosity", action="store_true")
    p("--reset", help="reset the library", action="store_true")
    args = parser.parse_args()
    quiet = args.quiet
    verbose = args.verbose
    reverse = args.reverse
    number = args.number or 5

    if not quiet: print("Rog's Plex Tools.")
    if verbose: print('Arguments:', args)

    data = update_media_records(update=args.update, reset=args.reset, verbose=verbose)

    if args.all:
        if verbose: print('Showing all items.')
        number = len(data)

    sort_criteria = []
    if args.pixels: sort_criteria.append('height')
    if args.size:   sort_criteria.append('size')
    if args.date:   sort_criteria.append('added')

    # setup default view
    if not sort_criteria:
        sort_criteria = [ 'added' ]
        reverse = True

    for s in sort_criteria:
        data = sort_by(data, attrib=s, reverse=reverse, verbose=verbose, quiet=quiet)

    if args.mpeg:
        show_uncompressed(data, verbose=verbose)

    if args.search:
        search = ' '.join(args.search).lower()
        matches = search_records(search, data, verbose=verbose)
    else:
        show_records(data, number=number, quiet=quiet, verbose=verbose, reverse=reverse, desc=sort_criteria)

    clock = time.perf_counter() - clock
    print(f'Total elapsed time: {showtime(clock)}.')


if __name__== "__main__" :
    main()