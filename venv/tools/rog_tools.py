import os, sys, time, pickle, random, argparse
#from tqdm import tqdm
#import pymediainfo
#from colorama import init, Fore
#init(autoreset=True)

def log(text):
    print(text)

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

def get_modified_time(path, str=False):
    ''' return modified file time of path, or zero if file does not exist '''
    if not os.path.exists(path):
        return 0
    t = os.path.getmtime(path)
    return time.ctime(t) if str else t

def get_all_files(root_dir : str, verbose=False, ignore = []) -> dict:
    ''' Returns a list of paths for all files recursively at root_dir '''
    clock = time.perf_counter()
    print(f'Getting all files from: "{root_dir}" ...Please wait...')
    path_list = []
    skipped_list = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            skip = False
            path = os.path.join(root, file)
            for i in ignore:
                if i in path:
                    skip = True
                    break
            if skip:
                skipped_list.append(path)
            else:
                path_list.append(path)
    clock = time.perf_counter() - clock
    clear_line()
    print(f'Got {len(path_list):,} and skipped {len(skipped_list):,} items in {showtime(clock)}.')
    if verbose: print(f'Skipped list: {skipped_list}')
    return path_list

def purge_files(path_list, purge_list, ignore_case = False):
    ''' Purge items in path_list matching text in the purge_list, returning a new list of remaining items '''
    errors_count = 0
    purged_count = 0
    new_list = []
    for index, path in enumberate(path_list):
        path_check = path.lower() if ignore_case else path
        if ignore_case: path = path.lower()
        for text in purge_list:
            deleted = False
            if ignore_case: text = text.lower()
            if text in path_check:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        purged_count += 1
                        deleted = True
                    except Exception as e:
                        log(f'Failed to purge {path}: {e}')
                        errors += 1
                else:
                    log(f'Unable to purge {path}: file not found.')
                    errors += 1
            if not deleted: new_list.append(path)
    log(f'Purged {purged} files with {errors} errors.')
    return new_list


def show_file_size(bytes, r=1):
    terabytes = bytes / (10 ** 12)
    if terabytes > 1: return f'{round(terabytes, r):,}TB'
    gigabytes = bytes / (10 ** 9)
    if gigabytes > 1: return f'{round(gigabytes, r):,}GB'
    megabytes = bytes / (10 ** 6)
    if megabytes > 1: return f'{round(megabytes, r):,}MB'
    kilobytes = bytes / (10 ** 3)
    if kilobytes > 1: return f'{round(kilobytes, r):,}kb'
    # else
    return f'{bytes} bytes'

def get_size_of_files(path_list):
    try:
        size = sum(os.path.getsize(path) for path in path_list)
    except Exception as e:
        print(f'Failed to get size of path_list: {e}')
        return
    print(show_file_size(size))
    return size

def showtime(s: float) -> str:
    """ return seconds (s) as H:M:S or seconds < 10 """
    if s < 0.1:
        return f'{s:.5f} seconds'
    elif  s < 100 :
        return f'{s:.2f} seconds'
    else:
        return datetime.timedelta(seconds=round(s))

def save_data(path, data):
    """ save data to path """
    if not path:
        log('Save data - no path given')
        return False
    if not data:
        log(f'No data to save to {path}')
        return False
    backup = path + '.bak'
    temp = path + '.tmp'
    if os.path.exists(temp): os.remove(temp)
    with open(temp, 'wb') as handle:
        pickle.dump(data, handle)
    if os.path.exists(backup): os.remove(backup)
    if os.path.exists(path): os.rename(path, backup)
    os.rename(temp, path)
    modified = get_modified_time(path,str=True)
    log(f'Saved {len(data):,} records to {path}, {modified}.')
    return True

def load_data(path):
    if not os.path.exists(path):
        log(f'No data file at {path}')
        return None
    modified = get_modified_time(path, str=True)
    with open(path, 'rb') as handle:
        try:
            data = pickle.load(handle)
        except Exception as e:
            log(f'FAILED TO LOAD: {path}: {e}')
            return None
    log(f'Loaded {len(data):,} records from {path}, last updated: {modified}')
    return data


def main():
    print("Rog's Tools.")
    return

    path_list = get_all_files('..')
    get_size_of_files(path_list)

if __name__== "__main__" :
    main()