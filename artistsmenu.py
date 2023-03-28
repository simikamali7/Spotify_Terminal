import login
import global_file
import sys

connection = global_file.connection
cursor = global_file.cursor

def add_song(aid):
    # add a song functionality by the artist
    global connection, cursor
    # is the song is already in
    song_is_in = True
    # if we continue
    if_con = False
    print("Please enter the title of the song: ")
    # ask for title
    title = input()
    title = title.strip()
    print("Please enter the duration of the song: ")
    duration = input()
    # ask for duration
    duration = duration.strip()
    # check if the song is already in
    cursor.execute('''select * from songs where LOWER(title) = LOWER(?) and duration = ?''', (title,duration))
    res = cursor.fetchall()
    if len(res) == 0:
        song_is_in = False
        if_con = True
    if song_is_in:
        print("*"*61)
        # if the song is already in
        print("The title and duration of the song is already in the database.")
        print("Please input r to reject it, or input a to add it as a new song.")
        ipt = input()
        options = ['r','a']
        # invalid input handling
        if ipt not in options:
            while True:
                print("Your input is not valid, please input again:")
                ipt = input()
                if ipt in options:
                    break
        if ipt == 'r':
            # reject the song
            print("*"*61)
            print("You have rejected the song.")
            print("To add a new song, please input a, to go to the art menu, please input m")
            ipt2 = input()
            options = ['a','m']
            if ipt2 not in options:
                while True:
                    print("Your input is not valid, please input again:")
                    ipt2 = input()
                    if ipt2 in options:
                        break
            if ipt2 == 'm':
                login.art_menu(aid)
            elif ipt2 == 'a':
                add_song(aid)
        elif ipt == 'a':
            # still want to continue
            if_con = True
    
    if if_con:
        cursor.execute('''select max(sid) from songs''')
        # Here I assigned the song id to be the largest song id +1, please inform me if you have better ideas
        max_id = cursor.fetchall()
        max_id = max_id[0][0]+1
        # insert the song 
        cursor.execute('''insert into songs values(:songid,:songtitle,:songdur)''',{"songid":max_id,"songtitle":title,"songdur":duration})
        # insert into perform
        cursor.execute('''insert into perform values(:artid,:songid)''',{"artid":aid,"songid":max_id})
        connection.commit()
        print("Is there any other artists have performed this song all together with you?")
        print("Enter y for yes and n for no")
        # check if other artists have involved in the perform
        y_n = input()
        if y_n != 'y' and y_n != 'n':
            while True:
              print("Your input is not valid, please enter y for yes and n for no!")
              y_n = input()
              if y_n == 'y' or y_n == 'n':
                break
        if y_n == 'n':
            # if there's not other artists that has been involved in the perform of this song
            print("You are all set! Your song has been perfectly added into the database!")
            print("Please input q to quit, l to logout,\na to add another song and z to go back to the last level")
            ipt = input()
            if ipt != 'a' and ipt != 'q' and ipt != 'l' and ipt != 'z':
                while True:
                    # invalid input handling
                    print("Your input is not valid, please enter again!")
                    ipt = input()
                    if ipt == 'a':
                        add_song(aid)
                    elif ipt == 'l':
                        login.main_interface()
                    elif ipt == 'q':
                        sys.exit(0)
                    elif ipt == 'z':
                        login.art_menu(aid)
            if ipt == 'a':
                # go back to add song
                add_song(aid)
            elif ipt == 'l':
                # go back to the main interface
                login.main_interface()
            elif ipt == 'q':
                # quit
                sys.exit(0)
            elif ipt == 'z':
                # go back to artist menu
                login.art_menu(aid)
        elif y_n == 'y':
            # add other artists
            add_mul_perform(aid,max_id)

def add_mul_perform(aid,songid):
    print("*"*61)
    print("Please enter the aids of the artists that you have collaborated with, split by comma:")
    aids = input()
    aid_lst = aids.split(',')
    for i in range(0,len(aid_lst)):
        temp = aid_lst[i]
        # check if that is a registered artist
        cursor.execute('''select * from artists a where a.aid=?''',(temp,))
        temp_lst = cursor.fetchall()
        connection.commit()
        if len(temp_lst) == 0:
            print("The aid you entered: "+temp+" is not an artist in our database")
            print("Please input q to quit, l to logout,\n a to input artist lists again and z to go back to the main menu")
            ipt = input()
            if ipt != 'a' and ipt != 'q' and ipt != 'l' and ipt != 'z':
                while True:
                    # invalid input handling
                    print("Your input is not valid, please enter again!")
                    ipt = input()
                    if ipt == 'a':
                        add_song(aid)
                    elif ipt == 'l':
                        login.main_interface()
                    elif ipt == 'q':
                        sys.exit(0)
                    elif ipt == 'z':
                        login.art_menu(aid)
            if ipt == 'a':
                # reinput
                add_mul_perform(aid,songid)
            elif ipt == 'l':
                # go back to the main interface
                login.main_interface()
            elif ipt == 'q':
                # quit
                sys.exit(0)
            elif ipt == 'z':
                # go back to the artist menu
                login.art_menu(aid)
            break

    for i in range(0,len(aid_lst)):
        temp = aid_lst[i]
        # insert into perform
        cursor.execute('''select * from perform p where p.aid = ? and p.sid = ?''',(temp,songid))
        temp_lst = cursor.fetchall()
        if len(temp_lst) != 0:
            continue
        else:
            cursor.execute('''insert into perform values(?,?)''',(temp,songid))
    
    connection.commit()
    print("All the aid has been added as a contributor to this song.")
    print("Enter l to logout, enter q to quit, enter b to go back to the main menu")
    l_q_b = input()
    options = ['l','q','b']
    if l_q_b not in options:
        # invalid input handling
        while True:
            print("Your input is not valid, please enter again.")
            l_q_b = input()
            if l_q_b in options:
                break
    if l_q_b == 'l':
        login.main_interface()
    elif l_q_b == 'q':
        sys.exit(0)
    elif l_q_b == 'b':
        login.art_menu(aid)

def find_top_fans(aid):
    # find top fans funtionality
    print("Your top 3 artists are: ")
    cursor.execute('''select uid from (
        select L.uid, (duration*cnt) as lenth from listen L, perform P, songs S
        where L.sid = P.sid
        and S.sid = L.sid
        and P.aid = '{}'
        group by L.uid,lenth
        order by lenth) 
        group by uid
        order by sum(lenth) desc
        limit 0,3;'''.format(aid))
    top_usrs = cursor.fetchall()
    for i in range(0,3):
        print("Top ",i+1,": ",str(top_usrs[i][0]))
    print("The top 3 playlists that include your songs most are:")
    cursor.execute('''select pid from (
        select pid,aid,count(aid) as ct from plinclude pl, perform p
        where pl.sid = p.sid
        and aid = '{}'
        group by pid,aid)
        order by ct desc
        limit 0,3;'''.format(aid))
    # top playlists
    top_ply = cursor.fetchall()
    for i in range(0,3):
        print("Top ",i+1,": ",str(top_ply[i][0]))
    
    print("\n")
    print("*"*61)
    print("To go back to the artist menu, please input m")
    print("To quit, input q, to logout, input l")
    ipt = input()
    options = ['m','q','l']
    if ipt not in options:
        while True:
            # invalid input handling
            print("Your input is not valid, please input a valid character again!")
            ipt = input()
            if ipt in options:
                break
    if ipt == 'm':
        login.art_menu(aid)
    elif ipt == 'q':
        sys.exit(0)
    elif ipt == 'l':
        login.main_interface()

