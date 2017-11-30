import _pickle as pickle

usersPath = './data/usersdata.pkl'
fansPath = './data/fansdata.pkl'

def getUser(username):
    users_dic = getUsers()
    return users_dic[username]

def getUsers(filePath=usersPath):
    try :
        with open(filePath, 'rb') as reader:
            return pickle.load(reader)
    except FileNotFoundError:
        return {}

def updateUser(user):
    users_dic = getUsers()
    users_dic[user.username] = user
    updateUsers(users_dic)

def updateUsers(users_dic,filePath=usersPath):
    with open(filePath, 'wb') as serializer:
        pickle.dump(users_dic, serializer, -1)



# ======================================
# def updateGames(games_dic, filePath=gamesPath):
#     with open(filePath, 'wb') as serializer:
#         pickle.dump(games_dic, serializer, -1)
#
# def updateGame(game):
#     games_dic = getAllGames()
#     games_dic[game.name] = game
#     updateGames(games_dic)
#
# def getGame(gameName):
#     games_dic = getAllGames()
#     return games_dic[gameName]
#
# def getAllGames(filePath=gamesPath):
#     try :
#         with open(filePath, 'rb') as reader:
#             return pickle.load(reader)
#     except FileNotFoundError:
#         return {}
#
# def getAllGamesNames():
#     return getAllGames().keys()
#
# def getPlayableGames():
#     completedGames_dic = {}
#     allGames_dic = getAllGames()
#     for gameName in allGames_dic:
#         if allGames_dic[gameName].playable:
#             completedGames_dic[gameName] = allGames_dic[gameName]
#     return completedGames_dic
#
# def getPlayableGamesNames():
#     return getPlayableGames().keys()
#
# def getUncompletedGames():
#     uncompletedGames_dic = {}
#     allGames_dic = getAllGames()
#     for gameName in allGames_dic:
#         if not allGames_dic[gameName].playable:
#             uncompletedGames_dic[gameName] = allGames_dic[gameName]
#     return uncompletedGames_dic
#
# def getUncompletedGamesNames():
#     return getUncompletedGames().keys()
#
#
# def getFans(filePath=fansPath):
#     try:
#         with open(filePath,'rb') as reader:
#             return pickle.load(reader)
#     except FileNotFoundError:
#         return {}
#
#
# def getFan(username):
#     fans_dic = getFans()
#     if username in fans_dic:
#         return fans_dic[username]
#     return False
#
# def updateFan(fan):
#     fans_dic = getFans()
#     fans_dic[fan.username] = fan
#     updateFans(fans_dic)
#
# def updateFans(fans_dic, filePath = fansPath):
#     with open(filePath, 'wb') as serializer:
#         pickle.dump(fans_dic, serializer, -1)
