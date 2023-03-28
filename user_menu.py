import login 
import global_file
import sys
import time

connection = global_file.connection
cursor = global_file.cursor


def reshape(lst):
    # reshape the one-dimensional array to a two dimensional array where each has a length of 5
    result = []
    index = 0
    for i in range(0,len(lst),5):
        if len(lst)-i < 5:
            temp = []
            for j in range(0,len(lst)-i):
                temp.append(lst[i+j])
        else:
            temp = []
            for j in range(5):
                temp.append(lst[i+j])
        result.append(temp)
        index +=1
    return result
        


# Start a session. The user should be able to start a session. 
# For each session, a session number unique for the user should be assigned by your system, 
# the session start date should be set to the current date and the session end date should be set to null.

# user can start session themselves
def start_session(uid):    
    global connection, cursor
    # make sure the sno is unique, we choose the max number and add 1 to it
    cursor.execute('''select max(sno) from sessions;''')
    max_sno = cursor.fetchall()[0][0]
    max_sno+=1
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    # insert a new session
    cursor.execute('''insert into sessions values (:uid,:sno,:start,null)''',{"uid":uid,"sno":max_sno,"start":current_date})
    connection.commit()
    print("*"*61)
    print("The session ",max_sno," has been created! ")
    login.usr_menu(uid)
    

# Search for songs and playlists. 
# The user should be able to provide one or more unique keywords, and the system should retrieve all songs and playlists that have any of those keywords in title. 
# For each matching song, the id, the title and the duration, and for each matching 
# playlist, the id, the title and the total duration of songs in the playlist should be returned. 
# Each row of the result should indicate if it is a song or a playlist. The result should be ordered based on the number of matching keywords 
# with songs/playlists that match the largest number of keywords listed on top. 
# If there are more than 5 matching songs/playlists, at most 5 matches will be shown at a time, 
# letting the user either select a match or see the rest of the matches in a paginated downward format. 
# If a playlist is selected, the id, the title and the duration of all songs in the playlist should be listed. 
# Any time a list of songs are displayed, the user should be able to select a song and perform a song action as discussed next. 
def search_songs_playlist(uid):
    print("Please enter the keyword to search in song or playlist.")
    
    keyword_ipt = input()
    kwd_lst = keyword_ipt.split(',')
    size = len(kwd_lst)
    for i in range(0,size):
        kwd_lst[i] = kwd_lst[i].strip()

    # construct the query for the retrieving songs
    query = '''select sid, title, duration, ('''

    for i in range(0,size):
        if i == size - 1:
            query += 'ct' + str(i+1) + ')'
        else:
            query += 'ct' + str(i+1) + '+'

    # query is the query to fetch all the matched result for song title, ordered by matches
    query += ''' as count from(
    select sid, title, duration, '''
    for i in range(0,size):
        if  i == size - 1:
            temp = "case when LOWER(title) LIKE '%{}%' then 1 else 0 end as ct{} ".format(kwd_lst[i],i+1)
            query+= temp
        else:
            temp = "case when LOWER(title) LIKE '%{}%' then 1 else 0 end as ct{}, ".format(kwd_lst[i],i+1)
            query+= temp

    query += '''FROM songs
    WHERE '''
    for i in range(0,size):
        if i == 0:
            temp = "title LIKE '% {}' OR title LIKE '{} %' OR title LIKE '% {} %'".format(kwd_lst[i],kwd_lst[i],kwd_lst[i])
            query += temp
        else:
            temp = "OR title LIKE '% {}' OR title LIKE '{} %' OR title LIKE '% {} %'".format(kwd_lst[i],kwd_lst[i],kwd_lst[i])
            query += temp

    query += '''
    group by sid, title, duration)
    order by count desc;
    '''
    cursor.execute(query)
    song_search = cursor.fetchall()

    # construct the query for the retrieving playlists
    # query2 is the query to fetch all the matched result for playlist title, ordered by matches
    query2 = '''select pl.pid, p.title, sum(s.duration) as len, ('''
    for i in range(0,size):
        if i == size - 1:
            query2 += "ct" + str(i+1) + ")"
        else :
            query2 += "ct" + str(i+1) + "+"
    query2 += ''' as count from(
    select pid, title, '''
    for i in range(0,size):
        if i == size - 1:
            temp = "case when LOWER(title) LIKE '%{}%'  then 1 else 0 end as ct{}".format(kwd_lst[i],i+1)
            query2 += temp
        else:
            temp = "case when LOWER(title) LIKE '%{}%'  then 1 else 0 end as ct{},".format(kwd_lst[i],i+1)
            query2 += temp
    query2 += '''
    FROM playlists
    WHERE '''
    for i in range(0,size):
        if i == 0:
            temp = "title LIKE '% {}' OR title LIKE '{} %' OR title LIKE '% {} %' ".format(kwd_lst[i],kwd_lst[i],kwd_lst[i])
            query2 += temp
        else:
            temp = " OR title LIKE '% {}' OR title LIKE '{} %' OR title LIKE '% {} %' ".format(kwd_lst[i],kwd_lst[i],kwd_lst[i])
            query2 += temp

    query2 += '''
    group by pid, title) p, plinclude pl, songs s
    where pl.pid = p.pid
    and s.sid = pl.sid
    group by pl.pid, p.title
    order by count desc;'''
    cursor.execute(query2)
    ply_search = cursor.fetchall()
    
    for i in range(0,len(song_search)):
        song_search[i] += ("song",)
    # song_search is the result searched for songs
    for i in range(0,len(ply_search)):
        ply_search[i] += ("playlist",)
    # ply_search is the result searched for playlists

    # Combine two lists
    for i in range(0,len(ply_search)):
        for j in range(0, len(song_search)):
            if song_search[j][3] <= ply_search[i][3]:
                song_search.insert(j,ply_search[i])
                break

    song_search = reshape(song_search)
    # If no result was returned
    if len(song_search) == 0:
        print("There's no such songs")
        login.usr_menu(uid)
    first_page = song_search[0]
    print("*"*61)
    # print the first page
    print("pid | songtitle | duration | type |")
    for i in range(len(first_page)):
        print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
    print("Page 1/",len(song_search))
    page = song_search[0]
    while True:
        print("To jump to a different page, please input a valid number between 1 -",len(song_search))
        print("To go back to the user menu, please input u, to select a song, please input s")
        ipt = input()
        option1 = []
        for i in range(1,len(song_search)+1):
            option1.append(str(i))
        option2 = ['u','s']
        # invalid input handling
        if (ipt not in option1) and (ipt not in option2):
            while True:
                print("Your input is not valid, please input again!")
                ipt = input()
                if (ipt in option1) or (ipt in option1):
                    break
        if ipt.isdigit():
            # if input is digit, then jump to that page
            print("*"*61)
            page = song_search[int(ipt)-1]
            print("pid | songtitle | duration | type |")
            for i in range(len(page)):
                print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][4])
            print("Page ",ipt,"/",len(song_search))
        else:
            # go back to user menu
            if ipt =='u':
                login.usr_menu(uid)
            elif ipt =='s':
                # select the song
                print("please input the order number of the song in this list")
                ipt2 = input()
                opt = []
                for i in range(1,len(page)+1):
                    opt.append(str(i))
                if ipt2 not in opt:
                    while True:
                        print("Your input is not valid, please input again")
                        ipt2 = input()
                        if ipt2 in opt:
                            break
                sl_song = page[int(ipt2)-1]
                # check if the selected is a song or playlists
                if sl_song[4] == 'song':
                    # song action
                    print("You have selected a song")
                    print("The song you have selected is:")
                    print(sl_song)
                    print("*"*61)
                    print("1. Listen")
                    print("2. See more information")
                    print("3. Add it to a playlist")
                    print("Input b to go back to the paginated list")
                    print("*"*61)
                    ipt4 = input()
                    op_song = ['1','2','3','b']
                    if ipt4 not in op_song:
                        while True:
                            print("Your input is not valid, please input again")
                            ipt4 = input()
                            if ipt4 in op_song:
                                break
                    if ipt4 == '1':
                        # listen
                        cursor.execute('''select * from sessions s
                                        where s.uid = :uid
                                        and s.end is null;''',{"uid":uid})
                        # check whether there's already a session
                        have_session =  cursor.fetchall()
                        if len(have_session) == 0:
                            # if not, create one
                            cursor.execute('''select max(sno) from sessions;''')
                            max_sno = cursor.fetchall()[0][0]
                            max_sno+=1
                            current_date = time.strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute('''insert into sessions values (:uid,:sno,:start,null)''',{"uid":uid,"sno":max_sno,"start":current_date})
                            connection.commit()
                            print("*"*61)
                            print("The session ",max_sno," has been created! ")
                            cursor.execute('''select * from sessions s
                                        where s.uid = :uid
                                        and s.end is null;''',{"uid":uid})
                            have_session =  cursor.fetchall()
                        sno = have_session[0][1]
                        sid = sl_song[0]
                        cursor.execute('''select * from listen
                                    where uid= :uid
                                    and sno = :sno
                                    and sid = :sid;''',{"uid":uid,"sno":sno,"sid":sid})
                        # check if the user have already listened to it before
                        have_listen = cursor.fetchall()
                        if len(have_listen) == 0:
                            cursor.execute('''insert into listen values (:uid,:sno,:sid,1.0);''',{"uid":uid,"sno":sno,"sid":sid})
                            connection.commit()
                            for i in range(len(first_page)):
                                print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                            print("Page 1/",len(song_search))
                        else:
                            # add one to cnt
                            cursor.execute('''update listen
                                            set cnt = :cnt
                                            where
                                            uid = :uid
                                            and sno = :sno
                                            and sid = :sid;''',{"cnt":have_listen[0][3]+1,"uid":uid,"sno":sno,"sid":sid})
                            connection.commit()
                            print("All set! Please input b to go back.")
                            ipt3 = input()
                            if ipt3!='b':
                                while True:
                                    print("Your input is not valid, input again")
                                    ipt3 = input()
                                    if ipt3 =='b':
                                        break
                            if ipt3 == 'b':
                                for i in range(len(first_page)):
                                    print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                                print("Page 1/",len(song_search))
                                continue
                    elif ipt4 == '2':
                        # fetch information details
                        cursor.execute('''select distinct a.name,s.*, pl.title from perform p, songs s, artists a, playlists pl, plinclude pi
                                        where p.sid = {}
                                        and s.sid = p.sid
                                        and a.aid = p.aid
                                        and pi.sid = s.sid
                                        and pl.pid = pi.pid;'''.format(sl_song[0]))
                        info_lst = cursor.fetchall() 
                        if info_lst == []:
                            print("No info")
                        for each in info_lst:
                            print(each,'|')
                        print("Input b to go back to the paginated songs")
                        ipt3 = input()
                        if ipt3!='b':
                            while  True:
                                print("Your input is not valid, input again")
                                ipt3 = input()
                                if ipt3 =='b':
                                    break
                        if ipt3 == 'b':
                            for i in range(len(first_page)):
                                print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                            print("Page 1/",len(song_search))
                            continue
                    elif ipt4 == '3':
                        # check if there's already a playlist
                        cursor.execute('''select * from playlists
                                where uid = :uid;''',{"uid":uid})
                        have_play = cursor.fetchall()

                        have_play_in = []
                        if (len(have_play) != 0):
                            # check if the song is already in the playlist
                            cursor.execute('''select * from plinclude pl
                                        where pid = :pid
                                        and sid = :sid;''',{"pid": have_play[0][0],"sid":sl_song[0]})
                            have_play_in = cursor.fetchall()
                        if ((not (len(have_play)==0)) and (len(have_play_in) != 0)) :
                            # if the song is already in the playlist, print already in
                            print("already in")
                        else:
                            if (not (len(have_play)==0)):
                                # if have a playlist, just insert the song
                                pid = have_play[0][0]
                                cursor.execute('''select max(p.sorder) from plinclude p
                                        where pid = :pid;''',{"pid":pid})
                                max = cursor.fetchall()[0]
                                max = max[0] + 1
                                cursor.execute('''insert into plinclude values(:pid,:sid,:order)''',{"pid":pid,"sid":sl_song[0],"order":max})
                                connection.commit()
                            else:
                                # if don't have a playlist, create one
                                cursor.execute('''select max(pid) from playlists''')
                                max = cursor.fetchall()[0][0]
                                max +=1
                                # get title
                                title_ipt = input("Please input a title: ")
                                cursor.execute('''insert into playlists values (:pid, :title, :uid)''',{"pid":max,"title":title_ipt,"uid":uid})
                                connection.commit()
                                print("A new playlist was created by you!")
                                cursor.execute('''insert into plinclude values(:pid,:sid,:sorder)''',{"pid":max,"sid":sl_song[0],"sorder":1})
                                connection.commit()
                                print("Added your sone to the new playlist")
                        print("Input b to go back to the paginated songs")
                        ipt3 = input()
                        if ipt3!='b':
                            while  True:
                                print("Your input is not valid, input again")
                                ipt3 = input()
                                if ipt3 =='b':
                                    break
                        if ipt3 == 'b':
                            for i in range(len(first_page)):
                                print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                            print("Page 1/",len(song_search))
                            continue
                    elif ipt4 == 'b':
                        for i in range(len(first_page)):
                            print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                        print("Page 1/",len(song_search))
                        continue
                elif sl_song[4] == 'playlist':
                    # playlist action
                    print("You have selected a playlist")
                    print("The playlist you have selected is:")
                    print(sl_song)
                    print("The songs in this playlist is:")
                    # fetch all the songs in the playlist
                    cursor.execute('''select distinct s.sid, s.title, s.duration from plinclude pl, songs s
                            where pl.pid = {}
                            and s.sid in (
                            select sid from plinclude pl2
                            where pl2.pid = {});'''.format(sl_song[0],sl_song[0]))
                    pl_detail = cursor.fetchall()
                    for each in pl_detail:
                        print(each)
                    print("Input b to go back to the paginated songs")
                    ipt3 = input()
                    if ipt3!='b':
                        while  True:
                            print("Your input is not valid, input again")
                            ipt3 = input()
                            if ipt3 =='b':
                                break
                    if ipt3 == 'b':
                        for i in range(len(first_page)):
                            print(first_page[i][0], " | ",first_page[i][1]," | ",first_page[i][2]," | ",first_page[i][4])
                        print("Page 1/",len(song_search))
                        continue

    
    

# Search for artists. 
# The user should be able to provide one or more unique keywords, and the system should retrieve all artists that have any
# of those keywords either in their names or in the title of a song they have performed. 
# For each matching artist, the name, the nationality and the number of songs performed are returned. 
# The result should be ordered based on the number of matching keywords with artists that match the largest number of keywords listed on top. 
# If there are more than 5 matching artists, at most 5 matches will be shown at a time, 
# letting the user either select a match for more information or see the rest of the matches in a paginated downward format. 
# The user should be able to select an artist and see the id, the title and the duration of all their songs. 
# Any time a list of songs are displayed, the user should be able to select a song and perform a song action as discussed next. 
def artist_search(uid):
    print("Please enter the keyword to search in song or playlist.")
    
    # get the keyword the user want to search for
    keyword_ipt = input()
    kwd_lst = keyword_ipt.split(',')
    size = len(kwd_lst)
    for i in range(0,size):
        kwd_lst[i] = kwd_lst[i].strip()
    temp = ""
    # construct query for artists search
    for i in range(size*2):
        if i != size*2-1:
            temp += "ct"+str(i+1) + "+"
        else:
            temp += "ct"+str(i+1)
    query3 = '''select aid,name,nationality, snum, ({}) as count from (
    select aid,name, nationality, snum, title, '''.format(temp)

    temp = ""
    # 0 - 1 - 2
    # 1 - 3 - 4
    for i in range(size):
        if i != size-1:
            temp = '''case when LOWER(name) LIKE '%{}%' then 1 else 0 end as ct{},
            case when LOWER(title) LIKE '%{}%' then 1 else 0 end as ct{},'''.format(kwd_lst[i],2*i+1,kwd_lst[i],2*i+2)
            query3+=temp
        else:
            temp = '''case when LOWER(name) LIKE '%{}%' then 1 else 0 end as ct{},
            case when LOWER(title) LIKE '%{}%' then 1 else 0 end as ct{}'''.format(kwd_lst[i],2*i+1,kwd_lst[i],2*i+2)
            query3+=temp
    temp = '''
    from
    (select distinct ar.aid, name, nationality, snum, title
    from artists ar,(
    select a.aid,count(distinct p.sid) as snum from artists a, perform p, songs s
    where a.aid = p.aid
    and s.sid = p.sid
    group by a.aid,name) as p1, perform pe, songs so
    where ar.aid = p1.aid
    and pe.sid = so.sid
    and p1.aid = pe.aid)
    where'''
    query3 += temp

    for i in range(size):
        if i == 0:
            temp = '''
            LOWER(name) LIKE '%{}%'
            OR LOWER(title) LIKE '%{}%' '''.format(kwd_lst[i],kwd_lst[i])
            query3+=temp
        else:
            temp = '''
            OR LOWER(name) LIKE '%{}%'
            OR LOWER(title) LIKE '%{}%' '''.format(kwd_lst[i],kwd_lst[i])
            query3 += temp
    query3 += ''')
    group by aid,name,nationality, snum 
    order by count desc;
    '''
    cursor.execute(query3)
    search_art = cursor.fetchall()
    search_art = reshape(search_art)
    # print(search_art)
    page = search_art[0]
    # print the first page of the paginated list
    print("aid | name | nationality | snum | matches")
    for i in range(len(page)):
        print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
    print("Page 1/",len(search_art))
    while True:
        print("To jump to a different page, please input a valid number between 1 -",len(search_art))
        print("To go back to the user menu, please input u, to select a song, please input s")
        ipt = input()
        option1 = []
        for i in range(1,len(search_art)+1):
            option1.append(str(i))
        option2 = ['u','s']
        if (ipt not in option1) and (ipt not in option2):
            while True:
                print("Your input is not valid, please input again!")
                ipt = input()
                if (ipt in option1) or (ipt in option1):
                    break
        if ipt.isdigit():
            # if the input is a number, jump to a page
            print("*"*61)
            page = search_art[int(ipt)-1]
            print("aid | name | nationality | snum | matches")
            for i in range(len(page)):
                print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
            print("Page ",ipt,"/",len(search_art))
        else:
            if ipt =='u':
                # go back to the user menu
                login.usr_menu(uid)
            elif ipt == 's':
                # if the user want to select a song
                print("please input the order number of the song in this list")
                ipt2 = input()
                opt = []
                for i in range(1,len(page)+1):
                    opt.append(str(i))
                # invalid input handling
                if ipt2 not in opt:
                    while True:
                        print("Your input is not valid, please input again")
                        ipt2 = input()
                        if ipt2 in opt:
                            break
                sl_art = page[int(ipt2)-1]
                print("*"*61)
                print("Your selected artist is: ")
                print(sl_art)
                print("*"*61)
                print("All the songs played by this artist is: ")
                # print the songs been selected
                aid = sl_art[0]
                cursor.execute('''select s.sid, title, duration from songs s, perform p
                                where p.sid = s.sid
                                and p.aid = :aid;''',{"aid":aid})
                art_songs = cursor.fetchall()
                print("sid | title | duration")
                # print all the songs performed the selected artist
                for i in range(len(art_songs)):
                    print(art_songs[i][0], " | ",art_songs[i][1]," | ",art_songs[i][2])
                print("To select a song, input s, to go back to the paginated result, input b")
                ipt2 = input()
                options = ['b','s']
                # invalid input handling
                if ipt2 not in options:
                    while True:
                        print("Your input is not valid,please input again")
                        ipt2 = input()
                        if ipt2 in options:
                            break
                
                if ipt2 == 'b':
                    # go back and print the first page
                    for i in range(len(page)):
                        print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                    print("Page ",ipt,"/",len(search_art))
                    continue
                elif ipt2 == 's':
                    # select a song performed by the artist
                    print("please input the order number of the song in this list")
                    ipt4 = input()
                    size = len(art_songs)
                    option_song = []
                    for i in range(size):
                        option_song.append(str(i+1))
                    # invalid input handling
                    if ipt4 not in option_song:
                        while True:
                            print("Your input is not valid,please input again")
                            ipt4 = input()
                            if ipt4 in option_song:
                                break
                    sl_song = art_songs[int(ipt4)-1]
                    # the selected song
                    print("The song you have selected is: ")
                    print(sl_song)
                    print("*"*61)
                    print("1. Listen")
                    print("2. See more information")
                    print("3. Add it to a playlist")
                    print("Input b to go back to the paginated list")
                    print("*"*61)
                    ipt4 = input()
                    op_song = ['1','2','3','b']
                    # invalid input handling
                    if ipt4 not in op_song:
                        while True:
                            print("Your input is not valid, please input again")
                            ipt4 = input()
                            if ipt4 in op_song:
                                break
                    if ipt4 == '1':
                        # listen
                        cursor.execute('''select * from sessions s
                                        where s.uid = :uid
                                        and s.end is null;''',{"uid":uid})
                        have_session =  cursor.fetchall()
                        # check whether the session has existed
                        if len(have_session) == 0:
                            # if not, create one
                            cursor.execute('''select max(sno) from sessions;''')
                            max_sno = cursor.fetchall()[0][0]
                            max_sno+=1
                            current_date = time.strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute('''insert into sessions values (:uid,:sno,:start,null)''',{"uid":uid,"sno":max_sno,"start":current_date})
                            connection.commit()
                            print("*"*61)
                            print("The session ",max_sno," has been created! ")
                            cursor.execute('''select * from sessions s
                                        where s.uid = :uid
                                        and s.end is null;''',{"uid":uid})
                            have_session =  cursor.fetchall()
                        sno = have_session[0][1]
                        sid = sl_song[0]
                        cursor.execute('''select * from listen
                                    where uid= :uid
                                    and sno = :sno
                                    and sid = :sid;''',{"uid":uid,"sno":sno,"sid":sid})
                        have_listen = cursor.fetchall()
                        # check if the user have listened to it
                        if len(have_listen) == 0:
                            # if not listened before, insert a new line
                            cursor.execute('''insert into listen values (:uid,:sno,:sid,1.0);''',{"uid":uid,"sno":sno,"sid":sid})
                            connection.commit()
                            print("aid | name | nationality | snum | matches")
                            for i in range(len(page)):
                                print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                        else:
                            # if listened before, update the cnt and increase it by 1
                            cursor.execute('''update listen
                                            set cnt = :cnt
                                            where
                                            uid = :uid
                                            and sno = :sno
                                            and sid = :sid;''',{"cnt":have_listen[0][3]+1,"uid":uid,"sno":sno,"sid":sid})
                            connection.commit()
                            print("All set! Please input b to go back.")
                            ipt3 = input()
                            if ipt3!='b':
                                while True:
                                    print("Your input is not valid, input again")
                                    ipt3 = input()
                                    if ipt3 =='b':
                                        break
                            if ipt3 == 'b':
                                print("aid | name | nationality | snum | matches")
                                for i in range(len(page)):
                                    print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                                continue
                    elif ipt4 == '2':
                        # fetch the information list
                        cursor.execute('''select distinct a.name,s.*, pl.title from perform p, songs s, artists a, playlists pl, plinclude pi
                                        where p.sid = {}
                                        and s.sid = p.sid
                                        and a.aid = p.aid
                                        and pi.sid = s.sid
                                        and pl.pid = pi.pid;'''.format(sl_song[0]))
                        info_lst = cursor.fetchall() 
                        if info_lst == []:
                            # if the fetched list has no element in it, print no info
                            print("No info")
                        for each in info_lst:
                            # print the info lisy
                            print(each,'|')
                        print("Input b to go back to the paginated songs")
                        ipt3 = input()
                        if ipt3!='b':
                            # invalid input handling
                            while  True:
                                print("Your input is not valid, input again")
                                ipt3 = input()
                                if ipt3 =='b':
                                    break
                        if ipt3 == 'b':
                            # print the first page and go back to the next round of loop
                            print("aid | name | nationality | snum | matches")
                            for i in range(len(page)):
                                print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                            continue
                    elif ipt4 == '3':
                        # check whether already have a plylist
                        cursor.execute('''select * from playlists
                                where uid = :uid;''',{"uid":uid})
                        have_play = cursor.fetchall()

                        have_play_in = []
                        if (len(have_play) != 0):
                            cursor.execute('''select * from plinclude pl
                                        where pid = :pid
                                        and sid = :sid;''',{"pid": have_play[0][0],"sid":sl_song[0]})
                                        # check if the song is already in the playlist
                            have_play_in = cursor.fetchall()
                        if ((not (len(have_play)==0)) and (len(have_play_in) != 0)) :
                            # if already a playlist in, print already in
                            print("already in")
                        else:
                            # insert a new song into the existed playlist
                            if (not (len(have_play)==0)):
                                pid = have_play[0][0]
                                cursor.execute('''select max(p.sorder) from plinclude p
                                        where pid = :pid;''',{"pid":pid})
                                max = cursor.fetchall()[0]
                                max = max[0] + 1
                                cursor.execute('''insert into plinclude values(:pid,:sid,:order)''',{"pid":pid,"sid":sl_song[0],"order":max})
                                connection.commit()
                            else:
                                # create a new playlist, and add the song into it
                                cursor.execute('''select max(pid) from playlists''')
                                max = cursor.fetchall()[0][0]
                                max +=1
                                title_ipt = input("Please input a title: ")
                                cursor.execute('''insert into playlists values (:pid, :title, :uid)''',{"pid":max,"title":title_ipt,"uid":uid})
                                connection.commit()
                                print("A new playlist was created by you!")
                                cursor.execute('''insert into plinclude values(:pid,:sid,:sorder)''',{"pid":max,"sid":sl_song[0],"sorder":1})
                                connection.commit()
                                print("Added your sone to the new playlist")
                        print("Input b to go back to the paginated songs")
                        ipt3 = input()
                        if ipt3!='b':
                            # invalid input handling
                            while  True:
                                print("Your input is not valid, input again")
                                ipt3 = input()
                                if ipt3 =='b':
                                    break
                        if ipt3 == 'b':
                            print("aid | name | nationality | snum | matches")
                            for i in range(len(page)):
                                print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                            print("Page ",ipt,"/",len(search_art))
                            continue
                    elif ipt4 == 'b':
                        print("aid | name | nationality | snum | matches")
                        for i in range(len(page)):
                            print(page[i][0], " | ",page[i][1]," | ",page[i][2]," | ",page[i][3]," | ",page[i][4])
                        print("Page ",ipt,"/",len(search_art))
                        continue



# End the session. 
# The user should be able to end the current session. 
# This should be recorded with the end date/time set to the current date/time. 
def end_session(uid):
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    # set current date to the end column
    cursor.execute('''update sessions set end = (?) where uid = (?) and end is null''',(current_date,uid))
    connection.commit()
    print("*"*61)
    print("Your Session has ended.")
    # go back
    login.usr_menu(uid)
