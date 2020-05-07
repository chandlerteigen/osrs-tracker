"""
Programmer: Chandler Teigen
Creation date: 4/27/2020
Last modified: 4/27/2020
Description:
    A command line interface that allows tracking and visualization
    of Old School Runescape account data.
"""

import os
import argparse
from OSRS_Hiscores import Hiscores
import json
from matplotlib import dates as matplotdates
from matplotlib import pyplot as plt
from datetime import datetime
import dateutil.parser


# looks up account in the hiscores for its type,
# and stores the data into a json file


record_dir = "records/"

stat_list = ['total', 'attack', 'defense', 'strength', 'hitpoints', 'ranged', 'prayer', 'magic', 'cooking' , 'woodcutting',
             'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining', 'herblore', 'agility', 'thieving',
             'slayer', 'farming', 'runecrafting', 'hunter', 'construction']
def plot(args):
    """
    :method:
        plot

    :description:
        Plots the players indicated stat in the indicated mode.

    :param args:
        args.plot contains the player name the stat and the mode

    :return:
        No return value.
    """
    player = args.plot[0]
    stat = args.plot[1]
    mode = args.plot[2]

    if mode == 'x':
        mode = 'experience'
    elif mode == 'l':
        mode = 'level'
    elif mode == 'r':
        mode = 'rank'
    else:
        print('plot mode '+ mode + ' is not supported.')
        print('Please use one of the following modes: x, l, r')
        return

    if stat not in stat_list:
        print(stat + ' is not a stat in Old School Runescape.')
        return

    data = load(player)
    stat_data = list()
    time_data = list()

    for point in data:
        stat_data.append(point[stat][mode])
        time_data.append(dateutil.parser.isoparse(point['date']))

    plt.plot_date(time_data, stat_data, 'r--')
    plt.ylabel(stat + ' ' + mode)
    plt.xlabel('time')
    plt.title(player + '\'s ' + stat + ' ' + mode)
    plt.show()

def load(player):
    """
    :method:
        load
    :description:
        loads all of the player's data into a list of
        dictionaries where each item in the list
        is a tracked record of stats at a certain time.
    :param player:
        The name of the player to be loaded.
    :return:
        A list of dictionaries of stats.
    """
    data_list = list()
    if os.path.isdir(record_dir + player + '/'):
        print('Loading data for ' + player)
        data_points = os.listdir(record_dir + player + '/')
        for point in data_points:
            with open(record_dir + player + '/' + point) as file:
                data = json.load(file)
                data_list.append(data)
    return data_list


def rename(args):
    """
    :method:
        rename

    :description:
        renames the account directory in the records_dir.
        This should be used when an account undergoes a
        name change before continuing to track the account.

    :param args:
        args.rename contains the old name and the new name.
    :return:
        No return value.
    """
    old_dir = args.rename[0]
    new_dir = args.rename[1]
    if os.path.isdir(record_dir + args.rename[0] + '/'):
        print('Renaming ' + old_dir + ' to ' + new_dir)
        os.rename(record_dir + old_dir, record_dir + new_dir)
    else:
        print(record_dir + args.rename[0] + '/' + ' is not currently being tracked')

def show():
    """
    :method:
        show

    :description:
        prints all of the directory (account) names in the record
        directory if it exists.

    :return:
        No return value.
    """
    if os.path.isdir(record_dir):
        tracked_accounts = os.listdir(record_dir)
        for acc in tracked_accounts:
            print(acc)
    else:
        print("Error: records directory does not exist.")

def track(args):
    """
    :method:
        track

    :description:
        The track method checks for the existence of the records directory and
        the account directory, creates them if necessary then generates a json file
        containing the current account data.

    :param args:
        args contains the account name and the account type.

    :return:
        No return value.
    """
    account = args.track[0]
    account_type = args.track[1]
    account = account.lower()

    # check for the existence of necessary directories
    if not os.path.isdir(record_dir):
        os.mkdir(record_dir)

    if not os.path.isdir(record_dir + account):
        os.mkdir(record_dir + account)

    # store hiscores data in dictionary using OSRS_Hiscores API
    hiscores = Hiscores(account, actype=account_type)
    date = str(datetime.now()).split(".")[0]
    hiscores.stats['date'] = date
    print("Recording stats of " + account + " as of " + date)

    with open(record_dir + hiscores.username + '/' + date.replace(' ', '_').replace(':', '-') + '.json', 'w') as outfile:
        json.dump(hiscores.stats, outfile, indent=True)


def main():

    parser = argparse.ArgumentParser(prog='osrs-tracker',
                                     usage='%(prog)s [options] path',
                                     description="A data tracker for Old School Runescape.")

    parser.add_argument("-t", "--track", type=str, nargs=2, metavar=('name', 'acctype'),
                        help='Adds a time point to the account\'s record. Creates a new record if necessary. acctype: N, IM, UIM, HIC')

    parser.add_argument("-s", "--show", type=str, nargs='*',
                        help="Shows all the accounts with records.")

    parser.add_argument("-d", "--delete", type=str, nargs=1,
                        metavar="account_name", default=None,
                        help="Deletes the specified account from records.")

    parser.add_argument("--rename", type=str, nargs=2,
                        metavar=('old_name', 'new_name'),
                        help="Renames the specified record (for use when account is renamed).")

    parser.add_argument("-p", "--plot", type=str, nargs=3, metavar=('name', 'stat', 'mode'),
                        help="""Plots the requested stat of the player in the given mode. Modes: x, l, r.
                              (exp, level, and rank)""")


    args = parser.parse_args()


    if args.track != None:
        track(args)
    elif args.show != None:
        show()
    elif args.rename != None:
        rename(args)
    elif args.plot != None:
        plot(args)

if __name__ == "__main__":
    main()