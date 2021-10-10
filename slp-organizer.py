from slippi import Game
from pathlib import Path
import re,os,time,multiprocessing as mp

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
Organizes the files into folders in terms of (user choice):
    - date
    - W/L/draw/unfinished
    - my char
    - opponent char

SOME TESTS:
Ryzen 5 3600X, 6 cores 12 threads
Single process: 500 files iterated per ~90 seconds (~333 files/minute, ~5.55 files/second)
Multiprocessing: 4136 files iterated in ~114 seconds (~2176 files/minute, ~36.26 files/second)

TO DO:
    - check if file is already where it belongs, to eliminate redundancy
    - check if file is netplay (mychar/oppchar don't work if it isn't)
'''

# define global constants
SLP_DIR = '/home/mire/Slippi/test/Pound-2019'
MY_CODE = 'MIRE#409'
NUM_PROCESSES = mp.cpu_count()


##########      begin defining functions        ##########
def iterate_group(group, classifier):
    """
    Iterates through SLP_DIR+'/tmp/' directory, then organizes .slp files found into
    corresponding folders based on date, match outcome, user character, or opponent character.
    """
    # for each file in that group
    for filename in group:
        # if the item is a slp replay
        if Path(filename).suffix == '.slp':
            curr_file = (SLP_DIR+'/tmp/'+filename)
            if os.path.isfile(curr_file):
                game = Game(curr_file)
                #print(game)
                # pull data based on classifier
                if classifier == 'date':    
                    date = re.findall('\d\d\d\d-\d\d-\d\d', str(game))[0]
                    print('file moved to ' + SLP_DIR+'/'+date+'/'+filename) # placeholder for moving file
                    try:
                        os.rename(curr_file, SLP_DIR+'/'+date+'/'+filename)
                    except FileNotFoundError:
                        os.mkdir(SLP_DIR+'/'+date)
                        os.rename(curr_file, SLP_DIR+'/'+date+'/'+filename)
                elif classifier == 'winloss':
                    pass #FIXME
                elif classifier == 'mychar':
                    players_section = re.findall('characters=.*\s+.*\s+.*\s', str(game))
                    chars = ['']*4
                    conn_codes = ['']*4
                    for i in range(len(players_section)):
                        chars[i] = re.findall('characters=.*:.*:', str(game))[i].replace('characters={'+str(i+1)+':', '').replace(':', '')
                        conn_codes[i] = re.findall('code=.*,', str(game))[i].replace('code=', '').replace(',', '')
                    for i in range(len(conn_codes)):
                        if conn_codes[i] == MY_CODE:
                            mychar = chars[i]
                    print(SLP_DIR+'/'+mychar+'-me/'+filename) # placeholder for moving file
                    #os.rename(curr_file, SLP_DIR+'/'+mychar+'-me/'+filename)
                elif classifier == 'oppchar':
                    players_section = re.findall('characters=.*\s+.*\s+.*\s', str(game))
                    chars = ['']*4
                    conn_codes = ['']*4
                    for i in range(len(players_section)):
                        chars[i] = re.findall('characters=.*:.*:', str(game))[i].replace('characters={'+str(i+1)+':', '').replace(':', '')
                        conn_codes[i] = re.findall('code=.*,', str(game))[i].replace('code=', '').replace(',', '')
                    for i in range(len(conn_codes)):
                        if conn_codes[i] != MY_CODE:
                            oppchar = chars[i]
                            break
                    print(SLP_DIR+'/'+oppchar+'-opp/'+filename) # placeholder for moving file
                    #os.rename(curr_file, SLP_DIR+'/'+oppchar+'-opp/'+filename)


def consolidate(dir):
    """
    Recursively iterates through directory, moving all files to tmp directory.
    """
    for item in os.listdir(dir):
        # if its a directory, recursively iterate through it
        if os.path.isdir(os.path.join(dir,item)):
            consolidate(os.path.join(dir,item))
        # if its a file, move it to tmp folder
        else:
            try:
                os.rename(os.path.join(dir,item), SLP_DIR+'/tmp/'+item)
            except FileNotFoundError:
                os.mkdir(SLP_DIR+'/tmp')
                os.rename(os.path.join(dir,item), SLP_DIR+'/tmp/'+item)
##########      END DEFINING FUNCTIONS          ##########

# user prompt
while True:
    choice = input('''\nChoose classifier by which to organize files:\n\n\t1. date
                                                                        \n\t2. win/loss/draw/unfinished (not implemented)
                                                                        \n\t3. my character (not implemented)
                                                                        \n\t4. opponent character (not implemented)
                                                                        \n> ''')
    if choice == '1':
        classifier = 'date'
        break
    elif choice == '2':
        classifier = 'winloss'
        break
    elif choice == '3':
        classifier = 'mychar'
        break
    elif choice == '4':
        classifier = 'oppchar'
        break
    else:
        print('Invalid answer.')

classifier = 'date' # only correctly implemented option

timestamp = time.time()
consolidate(SLP_DIR)
print('done consolidating files to tmp! total time:\t', time.time() - timestamp, 'seconds')
print('now dividing files in tmp into', NUM_PROCESSES, 'folders...')

print('\n')
all_filenames = [name for name in os.listdir(SLP_DIR+'/tmp/') if os.path.isfile(SLP_DIR+'/tmp/'+name)]
total_file_count = len(all_filenames)
group_size = int(total_file_count/NUM_PROCESSES)
print('file count:',total_file_count)
print('cpus:',NUM_PROCESSES)
print('group size:',group_size)
subgroups = [all_filenames[i:i+group_size] for i in range(0, len(all_filenames), group_size)]

processes = []
for i in range(len(subgroups)):
    processes.append(mp.Process(target=iterate_group, args=(subgroups[i], classifier)))
    processes[i].start()

for process in processes:
    process.join()

#os.rmdir(SLP_DIR+'/tmp/')
print('done!\n\t' + str(total_file_count) + ' files organized in ' + str(time.time() - timestamp) + ' seconds')
exit()