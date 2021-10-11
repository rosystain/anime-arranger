import sys, os, re, shutil
import xml.etree.ElementTree as ET
import urllib.request, time, sys
import configparser

def checkVersion():
    version_file = sys.path[0] + '/data/.version'
    if os.path.exists(version_file):
        with open(version_file) as version:
            fileDate = version.read()
        if  currentDate == fileDate:
            print('\nanime-list is up to date\n')
        else:
            updateAnimeList()
    else:
        updateAnimeList()

def updateAnimeList():
    checkDir(sys.path[0] + '/data/')
    try:
        print('updating anime-list.xml')
        response = urllib.request.urlopen('https://cdn.jsdelivr.net/gh11/Anime-Lists/anime-lists/anime-list.xml')
        r_list = response.read( )
        with open(sys.path[0] + '/data/anime-list.xml','wb') as list_file: list_file.write(r_list)
        print('updating animetitles.xml')
        response = urllib.request.urlopen('https://cdn.jsdelivr.net/gh11/Anime-Lists/anime-lists/animetitles.xml')
        r_title = response.read()
        with open(sys.path[0] + '/data/animetitles.xml','wb') as title_file: title_file.write(r_title)     
        with open(sys.path[0] + '/data/.version', 'w') as version: version.write(currentDate)
        print('\nAnimelist is up to date now\n')
    except urllib.error.URLError as e:
        print('Error in updating Animelist\n', e.reason, '\nUpdate Failed')


def fuzzyPattern(originalTitle):
    print('title:', originalTitle)
    pattern = re.sub(r'\W','.*', originalTitle)
    return pattern

def getAnidbID(pattern):
    tree = ET.parse(sys.path[0] + '/data/animetitles.xml')
    root = tree.getroot()
    suggestions = {}
    for child in root:
        for children in child:
            matchTitle = re.search(pattern, children.text, re.I)
            if matchTitle:
                suggestions[children.text] = child.attrib['aid']
    return suggestions[min(list(suggestions.keys()))]

def getRelationship(aid):
    tree = ET.parse(sys.path[0] + '/data/anime-list.xml')
    root = tree.getroot()
    for child in root:
        if aid == child.attrib['anidbid']: 
            return child.attrib

def checkDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def arrangeTorrent(torrentDir, torrentName):
    torrentPath = os.path.join(torrentDir, torrentName)
    originalTitle = os.path.basename(torrentDir.rstrip('/'))
    checkVersion()
    anidbID = getAnidbID(fuzzyPattern(originalTitle))
    if not anidbID == 'None': print('anidb-id:', anidbID)
    relationship = getRelationship(anidbID)
    '''
    if 'tvdbid' in relationship: 
        print('tvdb-id:', relationship['tvdbid'])
    if 'tmdbid' in relationship: 
        print('tmdb-id:', relationship['tmdbid'])
    if 'imdbid' in relationship: 
        print('imdb-id:', relationship['imdbid'])
    '''
    if 'defaulttvdbseason' in relationship: 
        print('season:', relationship['defaulttvdbseason'])
        seasonID = relationship['defaulttvdbseason']
    else: seasonID = '1'
    # deal with unfriendly filename format
    if os.path.isfile(torrentPath):
        filename = re.sub(r'\[(\d{2})\]', r' \1 ', torrentName)
        # move file
        config = configparser.ConfigParser()
        if  os.path.isfile('./config.ini'):
            config.read('./config.ini')
            mode = config['General']['ArchiveMode']
            if mode == '1': targetDir = os.path.join(config['General']['LibraryPath'], originalTitle) 
            else: targetDir = torrentDir
            shutil.move(torrentPath, os.path.join(checkDir(os.path.join(targetDir,'Season ' + seasonID)),filename))
            shutil.rmtree(torrentDir)
    else: print(torrentPath, 'is not a file!')

if __name__ == '__main__':
    torrentDir = sys.argv[1]
    torrentName = sys.argv[2]
    torrentPath = os.path.join(torrentDir, torrentName)
    currentDate = time.strftime("%Y-%m-%d", time.localtime())
    
    arrangeTorrent(torrentDir, torrentName) 
