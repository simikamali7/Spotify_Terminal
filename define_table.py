import sqlite3
connection = sqlite3.connect('prj-test.db')
cursor= connection.cursor()
def define_tables():
    global connection, cursor
    users = '''create table users (
        uid  char(4),
        name  text,
        pwd  text,
        primary key (uid)
        );
    '''
    songs = '''create table songs (
        sid  int,
        title  text,
        duration  int,
        primary key (sid)
        );'''
    sessions = '''create table sessions (
        uid  char(4),
        sno  int,
        start  date,
        end  date,
        primary key (uid,sno),
        foreign key (uid) references users on delete cascade
        );'''
    listen = '''create table listen (
        uid  char(4),
        sno  int,
        sid  int,
        cnt  real,
        primary key (uid,sno,sid),
        foreign key (uid,sno) references sessions,
        foreign key (sid) references songs
        );'''
    playlist = '''create table playlists (
        pid  int,
        title  text,
        uid  char(4),
        primary key (pid),
        foreign key (uid) references users
        );'''
    plinclude = '''create table plinclude (
        pid  int,
        sid  int,
        sorder  int,
        primary key (pid,sid),
        foreign key (pid) references playlists,
        foreign key (sid) references songs
        );'''
    artists = '''create table artists (
        aid  char(4),
        name  text,
        nationality text,
        pwd  text,
        primary key (aid)
        );'''
    perform = '''create table perform (
        aid  char(4),
        sid  int,
        primary key (aid,sid),
        foreign key (aid) references artists,
        foreign key (sid) references songs
        );'''
    cursor.execute(users)
    cursor.execute(songs)
    cursor.execute(sessions)
    cursor.execute(listen)
    cursor.execute(playlist)
    cursor.execute(plinclude)
    cursor.execute(artists)
    cursor.execute(perform)
    connection.commit()
    return

define_tables()