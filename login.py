import time
import os
import tables
import global_file
import sqlite3
import sys
import artistsmenu
import user_menu
import getpass
# import IcantTellUThat from Davood

connection = global_file.connection
cursor = global_file.cursor

def main_interface():
    # the main interface of the whole program
    print("*"*61)
    print("*"*5+" Welcome to our CMPUT291 mini-project1 application "+"*"*5)
    print("*"*61+"\n")
    print("1. Login")
    print("2. Register account")
    print("3. Exit\n\n")
    print("*"*61)
    print("Please enter the number before the option you want to select and press enter...")
    dec_num = input()
    # invalid input handling
    if (dec_num != '1' and dec_num != '2' and dec_num != '3'):
        while True:
            print("Your input is not valid, please enter again!")
            dec_num = input()
            if (dec_num == '1' or dec_num == '2'or dec_num == '3'):
                break
    if (dec_num == '1'):
        # jump to login function
        user_login()
    elif (dec_num == '2'):
        # jump to user register
        user_register()
    else:
        # quit
        sys.exit(0)

def user_register():
    is_valid = False
    print("*"*61)
    print("Please enter the userid you wish to signup for:")
    usr_id = input()
    # check whether the id is in user table
    cursor.execute('''select * from users U where U.uid = ?''',(usr_id,))
    rst_lst = cursor.fetchall()
    # check whether the id is in artists table
    cursor.execute('''select * from artists a where a.aid = ?''',(usr_id,))
    rst_lst2 = cursor.fetchall()
    if (len(rst_lst) == 0 and len(rst_lst2) == 0 ):
        is_valid = True
    if (not is_valid):
        while True:
            # invalid id handling
            print("Your user id has been occupied by someone else, please enter another one:")
            usr_id = input()
            cursor.execute('''select * from users U where U.uid = ?''',(usr_id,))
            rst_lst = cursor.fetchall()
            cursor.execute('''select * from artists a where a.aid = ?''',(usr_id,))
            rst_lst2 = cursor.fetchall()
            connection.commit()
            if (len(rst_lst) == 0 and len(rst_lst2) == 0):
                is_valid = True
            if is_valid: break
    # get username
    print("Please enter the username you wish to signup for:")
    usr_name = input()
    # get password
    print("Please enter the password you wish to set:")
    usr_pwd = getpass.getpass()
    cursor.execute('''insert into users values(:uid,:uname,:upwd)''',{"uid":usr_id,"uname":usr_name,"upwd":usr_pwd})
    connection.commit()
    print("You are all set!")
    print("*"*61)
    print("Welcome! User '{}'".format(usr_id))
    print("Hit enter to go to the user menu.")
    print("Input 'q' to quit, or l to logout")
    q_l_en = input()
    if q_l_en == 'q':
        # quit
        sys.exit(0)
    elif q_l_en == 'l':
        # go back to the main interface
        main_interface()
    elif len(q_l_en) == 0:
        # go to the user menu
        usr_menu(usr_id)
    else:
        while True:
            # invalid input handling
            print("Your input is not valid, please enter again!")
            q_l_en = input()
            if q_l_en == 'q':
                sys.exit(0)
            elif q_l_en == 'l':
                main_interface()
            elif len(q_l_en) == 0:
                usr_menu(usr_id)


def art_menu(aid):
    # art menu interface
    print("*"*61)
    print("Welcome to the artists menu!")
    print("1. Add a song")
    print("2. Find top fans and playlists")
    print("3. Logout")
    print("4. Exit")
    print("Please enter the number before the option you want to select and press enter...")
    art_num = input()
    options = ['1','2','3','4']
    # invalid input handling
    if art_num not in options:
        while True:
            print("Your input is not valid, please double check and enter again!")
            art_num = input()
            if art_num in options:
                break
    if art_num == '1':
        # jump to add a song functionality
        artistsmenu.add_song(aid)
    elif art_num == '2':
        # jump to find top fans functionality
        artistsmenu.find_top_fans(aid)
    elif art_num == '3':
        # go back to the main interface
        main_interface()
    elif art_num == '4':
        # quit
        sys.exit(0)
    

def usr_menu(uid):
    # the main interface for the user
    print("*"*61)
    print("Welcome to the users menu!")
    print("1. Start a session")
    print("2. Search for songs and playlists")
    print("3. Search for artists")
    print("4. End the session")
    print("5. Logout")
    print("6. Exit")
    print("Please enter the number before the option you want to select and press enter...")
    usr_num = input()
    options = ['1','2','3','4','5','6']
    # invalid input handling
    if usr_num not in options:
        while True:
            print("Your input is not valid, please double check and enter again!")
            usr_num = input()
            if usr_num in options:
                break
    if usr_num == '1':
        # jump to the start session functionality
        user_menu.start_session(uid)
    elif usr_num == '2':
        # jump to the search song playlists functionality
        user_menu.search_songs_playlist(uid)
    elif usr_num == '3':
        # jump to the artist search functionality
        user_menu.artist_search(uid)
    elif usr_num == '4':
        # jump to the end session functionality
        user_menu.end_session(uid)
    elif usr_num == '5':
        # if the user want to logout, end their session first
        current_date = time.strftime("%Y-%m-%d %H:%M:%S")
        # cursor.execute('''select sno from sessions where uid = :uid''')
        cursor.execute('''update sessions set end = (?) where uid = (?) and end is null''',(current_date,uid))
        connection.commit()
        print("*"*61)
        print("Your Session has ended.")
        # then go back to the main interface
        main_interface()
    elif usr_num == '6':
        #  if the user wnat to quit, end their session first
        current_date = time.strftime("%Y-%m-%d %H:%M:%S")
        # cursor.execute('''select sno from sessions where uid = :uid''')
        cursor.execute('''update sessions set end = (?) where uid = (?) and end is null''',(current_date,uid))
        connection.commit()
        print("*"*61)
        print("Your Session has ended.")
        # then quit
        sys.exit(0)


def user_login():
    # the user login interface
    global cursor,connection
    is_user = False
    is_art = False
    print("Please enter your user id:")
    # ask for uid
    uid = input()
    print("Please enter your password")
    # ask for password, used getpass library to make sure password input invisible
    pwd = getpass.getpass()
    # print(uid)
    # print(pwd)

    # print(cursor,connection)
    # check if the uid and pwd is valid
    cursor.execute('''select * from users U where U.uid = :userid and U.pwd == :userpwd''',{"userid":uid,"userpwd":pwd})
    connection.commit()
    rst = cursor.fetchall()
    
    if len(rst) ==1:
        is_user = True
    
    # checkif the aid and pwd is valid
    cursor.execute('''select * from artists A where A.aid = :artid and A.pwd == :artpwd''',{"artid":uid,"artpwd":pwd})
    connection.commit()
    rst = cursor.fetchall()
    
    if len(rst) == 1:
        is_art = True
    
    if (is_art and (not(is_user))):
        # login as artist
        print("*"*61)
        print("Welcome! Artist '{}'".format(uid))
        print("Hit enter to go to the user menu.")
        print("Input 'q' to quit, or l to logout")
        q_l_en = input()
        if q_l_en == 'q':
            sys.exit(0)
        elif q_l_en == 'l':
            main_interface()
        elif len(q_l_en) == 0:
            art_menu(uid)
        else:
            # invalid input handling
            while True:
                print("Your input is not valid, please enter again!")
                q_l_en = input()
                if q_l_en == 'q':
                    sys.exit(0)
                elif q_l_en == 'l':
                    main_interface()
                elif len(q_l_en) == 0:
                    art_menu(uid)
    elif (is_user and (not(is_art))):
        # login as user
        print("Welcome! User '{}'".format(uid))
        print("Hit enter to go to the user menu.")
        print("Input 'q' to quit, or l to logout")
        q_l_en = input()
        if q_l_en == 'q':
            sys.exit(0)
        elif q_l_en == 'l':
            main_interface()
        elif len(q_l_en) == 0:
            usr_menu(uid)
        else:
            while True:
                # invalid input handling
                print("Your input is not valid, please enter again!")
                q_l_en = input()
                if q_l_en == 'q':
                    sys.exit(0)
                elif q_l_en == 'l':
                    main_interface()
                elif len(q_l_en) == 0:
                    usr_menu(uid)
    elif (is_user and is_art):
        print("*"*61)
        # if the user is both an artist and a user
        print("You are both a user and an artist, which account do you wish to login?")
        print("Input 1 to login as a user")
        print("And input 2 to login as an artist")
        a_or_u = input()
        if (a_or_u != '1' and a_or_u != '2'):
            while True:
                print("Your input is not valid, please enter again!")
                a_or_u = input()
                if (a_or_u == '1' or a_or_u == '2'):
                    break
        if (a_or_u == '1'):
            print("Welcome! User '{}'".format(uid))
            print("Hit enter to go to the user menu.")
            print("Input 'q' to quit, or l to logout")
            q_l_en = input()
            if q_l_en == 'q':
                sys.exit(0)
            elif q_l_en == 'l':
                main_interface()
            elif len(q_l_en) == 0:
                usr_menu(uid)
            else:
                while True:
                    # invalid input handling
                    print("Your input is not valid, please enter again!")
                    q_l_en = input()
                    if q_l_en == 'q':
                        sys.exit(0)
                    elif q_l_en == 'l':
                        main_interface()
                    elif len(q_l_en) == 0:
                        usr_menu(uid)
        else:
            # direct the artist to the artist menu
            print("Welcome! Artist '{}'".format(uid))
            print("Hit enter to go to the artist menu.")
            print("Input 'q' to quit, or l to logout")
            q_l_en = input()
            if q_l_en == 'q':
                sys.exit(0)
            elif q_l_en == 'l':
                main_interface()
            elif len(q_l_en) == 0:
                art_menu(uid)
            else:
                while True:
                    print("Your input is not valid, please enter again!")
                    q_l_en = input()
                    if q_l_en == 'q':
                        sys.exit(0)
                    elif q_l_en == 'l':
                        main_interface()
                    elif len(q_l_en) == 0:
                        art_menu(uid)
    else:
        print("*"*61)
        # invalid match of the user id or artist id and their pwd
        print("Your id and password doesn't match any of our users")
        print("Please press q to quit, r to start over, and s to register an account")
        q_r_s = input()
        if (q_r_s != 'q' and q_r_s != 'r' and q_r_s != 's'):
            while True:
                print("Your input is invalid, please enter again")
                q_r_s = input()
                if q_r_s == 'q':
                    sys.exit(0)
                elif q_r_s == 'r':
                    user_login()
                elif q_r_s == 's':
                    user_register()
        if q_r_s == 'q':
            sys.exit(0)
        elif q_r_s == 'r':
            user_login()
        elif q_r_s == 's':
            user_register()





