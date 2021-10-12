'''
PROGRAM:
slp-organizer

AUTHOR:
mire

NOTES:
Not sure if it's that useful, but a good exercise in parsing SLP replays.
Hogs resources pretty hard, probably pushes your CPU to 100% utilization.

DESCRIPTION:
Iterates through all .slp files found in master SLP_DIR directory.
Organizes the files into subdirectories in terms of (user choice):
    - date
    - W/L/other
    - my char
    - opponent char

SOME TESTS:
Ryzen 5 3600X, 6 cores 12 threads
Single process: 500 files iterated per ~90 seconds (~333 files/minute, ~5.55 files/second)
Multiprocessing: 4136 files iterated in ~114 seconds (~2176 files/minute, ~36.26 files/second)

TO DO:
    - look into changing os.rename command based on user OS
    - check if file is already where it belongs, to eliminate redundancy
    - add progress bar :D
    - try to do something about date conversion from UTC... or just don't bother
    - convert to GUI app, maybe with Gooey
'''

from slippi import Game
from pathlib import Path
from time import sleep,time
import re,os,time,multiprocessing as mp,glob,sys
_OS = sys.platform
if _OS != 'linux' and _OS != 'win32':
    exit('OS not recognized or not supported.\n')


##########      begin defining functions        ##########
def iterate_group(group, classifier, SLP_DIR, MY_CODE):
    """
    Iterates through group of files, then organizes .slp files found into
    corresponding subdirectories based on date, match outcome, user character, or opponent character.
    """
    # for each file in that group
    for filepath in group:
        # if the item is a slp replay
        if Path(filepath).suffix == '.slp':
            curr_file = filepath
            if _OS == 'linux':
                filename = filepath.split('/')[-1]
            elif _OS == 'win32':
                filename = filepath.split('\\')[-1]
            if os.path.isfile(curr_file):
                game = Game(curr_file)
                #print(game)
                # pull data based on classifier
                # choice 1: date
                if classifier == 'date':    
                    date = re.findall('\d\d\d\d-\d\d-\d\d', str(game))[0]
                    #print('file moved to ' + SLP_DIR+'/'+date+'/'+filename) # debug output
                    try:
                        if _OS == 'linux':
                            os.rename(curr_file, SLP_DIR+'/'+date+'-matches/'+(filename))
                        elif _OS == 'win32':
                            os.rename(curr_file, SLP_DIR+'\\'+date+'-matches\\'+(filename))
                    except FileNotFoundError:
                        if _OS == 'linux':
                            os.mkdir(SLP_DIR+'/'+date+'-matches/')
                            os.rename(curr_file, SLP_DIR+'/'+date+'-matches/'+filename)
                        elif _OS == 'win32':
                            os.mkdir(SLP_DIR+'\\'+date+'-matches\\')
                            os.rename(curr_file, SLP_DIR+'\\'+date+'-matches\\'+filename)

                # choice 2: win/loss/other
                elif classifier == 'winloss':
                    pass #FIXME
                # choice 3: user's character or opponent's character
                elif classifier == 'mychar' or classifier == 'oppchar':
                    platform = re.findall('platform=.*,', str(game))[0].replace('platform=','').replace(',','')
                    dolphin = False
                    try:
                        re.findall('DOLPHIN', platform)[0]
                        dolphin = True
                    except IndexError:
                        dolphin = False
                    if dolphin:
                        players_section = re.findall('characters=.*\s+.*\s+.*\s', str(game))
                        chars = ['']*4
                        conn_codes = ['']*4
                        char = ''
                        for i in range(len(players_section)):
                            chars[i] = re.findall('characters=.*:.*:', str(game))[i].replace('characters={', '').replace(':', '')
                            conn_codes[i] = re.findall('code=.*,', str(game))[i].replace('code=', '').replace(',', '')
                        for i in range(len(conn_codes)):
                            if classifier == 'mychar' and conn_codes[i] == MY_CODE:
                                char = ''.join([i for i in chars[i] if not i.isdigit()])
                                break
                            if classifier == 'oppchar' and conn_codes[i] != MY_CODE:
                                char = ''.join([i for i in chars[i] if not i.isdigit()])
                                break
                        label = ''
                        if char != '':
                            if classifier == 'mychar':
                                label = '-me'
                            elif classifier == 'oppchar':
                                label = '-opp'
                            #print(SLP_DIR+'/'+char+label+filename) # debug output
                            if label != '':
                                try:
                                    if _OS == 'linux':
                                        os.rename(curr_file, SLP_DIR+'/'+char+label+'/'+filename)
                                    elif _OS == 'win32':
                                        os.rename(curr_file, SLP_DIR+'\\'+char+label+'\\'+filename)
                                except FileNotFoundError:
                                    if _OS == 'linux':
                                        os.mkdir(SLP_DIR+'/'+char+label)
                                        os.rename(curr_file, SLP_DIR+'/'+char+label+'/'+filename)
                                    elif _OS == 'win32':
                                        os.mkdir(SLP_DIR+'\\'+char+label)
                                        os.rename(curr_file, SLP_DIR+'\\'+char+label+'\\'+filename)

def consolidate(dir):
    """
    Recursively iterates through directory, adding all .slp files to master list.
    """
    for item in os.listdir(dir):
        # if its a directory, recursively iterate through it
        if os.path.isdir(os.path.join(dir,item)):
            consolidate(os.path.join(dir,item))
        # if its a file, append to files list
        else:
            if Path(item).suffix == '.slp':
                all_replay_files.append(str(os.path.join(dir,item)))

def progress(duration):
    value = 1
    size = 50 # number of * in progress bar
    print()
    timestamp = time()
    while value <= size:
        print('|' + '*'*value + ' '*(size-value) + '|  ' + str(round(value/size*100)) + '%\ttime left: ' + str(int(duration)-(round(time() - timestamp))) + 's', end='   \r')
        sleep(duration/size)
        value+=1
    print('\n')
##########      END DEFINING FUNCTIONS          ##########

if __name__ == '__main__':
    #SLP_DIR = '/home/mire/code/slp-organizer/500-item-test' # my test
    SLP_DIR = input('\nEnter full path to your Slippi .slp directory: ')
    if SLP_DIR[-1] == '/':
        SLP_DIR = SLP_DIR[:-1]
    MY_CODE = ''
    NUM_PROCESSES = mp.cpu_count()
    # recursively gather all .slp files in all subdirectories into one list
    all_replay_files = []
    consolidate(SLP_DIR)
    total_file_count = len(all_replay_files)

    if total_file_count == 0:
        print('No .slp files found in given directory. Exiting...\n')
        exit()
    else:
        print('\nDone gathering',total_file_count,'.slp files!')

    # user prompt
    while True:
        choice = input('''\nChoose classifier by which to organize files:\n\n\t1. date\n\t2. win/loss/other (not implemented)\n\t3. my character\n\t4. opponent character\n> ''')
        if choice == '1':
            _classifier = 'date'
            break
        elif choice == '2':
            _classifier = 'winloss'
            break
        elif choice == '3' or choice == '4':
            if choice == '3':
                _classifier = 'mychar'
            elif choice == '4':
                _classifier = 'oppchar'
            MY_CODE = input('Enter your connect code (ex: MIRE#409): ')
            # valid input of MY_CODE
            try:
                if len(re.findall('.+#[0-9]+', MY_CODE)[0]) > 8:
                    raise IndexError
            except IndexError:
                exit('Invalid code.\n')
            break

    
    # start time
    timestamp = time.time()

    # prepare int(NUM_PROCESSES) groups of files, print info
    group_size = int(total_file_count/(NUM_PROCESSES-1))
    print('\nfile count:',total_file_count)
    print('number of processes to be started:',NUM_PROCESSES)
    try:
        input('\nPress ENTER to continue, CTRL-C to exit...')
    except KeyboardInterrupt:
        exit('\n')
    subgroups = [all_replay_files[i:i+group_size] for i in range(0, len(all_replay_files), group_size)]

    # start organizing files using int(NUM_PROCESSES) processes
    processes = []
    for i in range(len(subgroups)):
        processes.append(mp.Process(target=iterate_group, args=(subgroups[i], _classifier, SLP_DIR, MY_CODE)))
        processes[i].start()
    for process in processes:
        process.join()

    # clean up now-empty folders
    if _classifier == 'date':
        empty_folders = glob.glob(SLP_DIR+'/*-opp/') + glob.glob(SLP_DIR+'/*-me/')
        for item in empty_folders:
            os.rmdir(item)
    elif _classifier == 'mychar':
        empty_folders = glob.glob(SLP_DIR+'/*-opp/') + glob.glob(SLP_DIR+'/*-*-*-matches/')
        for item in empty_folders:
            os.rmdir(item)
    elif _classifier == 'oppchar':
        empty_folders = glob.glob(SLP_DIR+'/*-me/') + glob.glob(SLP_DIR+'/*-*-*-matches/')
        for item in empty_folders:
            os.rmdir(item)

    # print info on exit
    print('\ndone!\t' + str(total_file_count) + ' files organized in ' + str(round(time.time() - timestamp, 3)) + ' seconds')
    exit()