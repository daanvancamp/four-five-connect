from time import sleep
import numpy as np
import pickle
from threading import Thread

overwrite=''


BOARD_ROWS = 13
BOARD_COLS = 13
lengte_winnen=5

class State:
    
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash

    def winner(self):
        # rijen
        for i in range(BOARD_ROWS):
            aantal_v_positief = 0
            aantal_v_negatief = 0
            for j in range(BOARD_COLS):
                if self.board[i][j] == 1:
                    aantal_v_positief += 1
                    aantal_v_negatief = 0
                elif self.board[i][j] == -1:
                    aantal_v_negatief += 1
                    aantal_v_positief = 0
                else:
                    aantal_v_positief = 0
                    aantal_v_negatief = 0

                if aantal_v_positief >= lengte_winnen:
                    self.isEnd = True
                    return 1
                if aantal_v_negatief >= lengte_winnen:
                    self.isEnd = True
                    return -1

        # kolommen
        for j in range(BOARD_COLS):
            aantal_h_positief = 0
            aantal_h_negatief = 0
            for i in range(BOARD_ROWS):
                if self.board[i][j] == 1:
                    aantal_h_positief += 1
                    aantal_h_negatief = 0
                elif self.board[i][j] == -1:
                    aantal_h_negatief += 1
                    aantal_h_positief = 0
                else:
                    aantal_h_positief = 0
                    aantal_h_negatief = 0

                if aantal_h_positief >= lengte_winnen:
                    self.isEnd = True
                    return 1
                if aantal_h_negatief >= lengte_winnen:
                    self.isEnd = True
                    return -1
        aantal_diag_positief = 0
        aantal_diag_negatief = 0
        # diagonalen
        for i in range(BOARD_ROWS - lengte_winnen + 1):
            for j in range(BOARD_COLS - lengte_winnen + 1):
                # check diagonalen van linksboven naar rechtsonder
                for k in range(lengte_winnen):
                    if self.board[i + k][j + k] == 1:
                        aantal_diag_positief += 1
                        aantal_diag_negatief = 0
                    elif self.board[i + k][j + k] == -1:
                        aantal_diag_negatief += 1
                        aantal_diag_positief = 0
                    else:
                        aantal_diag_positief = 0
                        aantal_diag_negatief = 0

                    if aantal_diag_positief >= lengte_winnen:
                        self.isEnd = True
                        return 1
                    if aantal_diag_negatief >= lengte_winnen:
                        self.isEnd = True
                        return -1

                # check diagonalen van rechtsboven naar linksonder
                for k in range(lengte_winnen):
                    if self.board[i + k][j + lengte_winnen - 1 - k] == 1:
                        aantal_diag_positief += 1
                        aantal_diag_negatief = 0
                    elif self.board[i + k][j + lengte_winnen - 1 - k] == -1:
                        aantal_diag_negatief += 1
                        aantal_diag_positief = 0
                    else:
                        aantal_diag_positief = 0
                        aantal_diag_negatief = 0

                    if aantal_diag_positief >= lengte_winnen:
                        self.isEnd = True
                        return 1
                    if aantal_diag_negatief >= lengte_winnen:
                        self.isEnd = True
                        return -1

        # gelijkspel
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0

        # niet het einde
        self.isEnd = False
        return None


    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions

    def updateState(self, position):
        self.board[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif result == -1:
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    def play(self, rounds=100):
        for i in range(rounds):
            if i % 1000 == 0:
                print("Rounds {}".format(i))
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end

                win = self.winner()
                if win is not None:
                    # self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
            # take action and upate board state
            self.updateState(p1_action)
            self.showBoard()
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self):
        # p1: x  p2: o
        for i in range(0, BOARD_ROWS):
            print(5*'---------------')
            out = '| '
            for j in range(0, BOARD_COLS):
                if self.board[i, j] == 1:
                    token = 'x'
                if self.board[i, j] == -1:
                    token = 'o'
                if self.board[i, j] == 0:
                    token = ' '
                out += token + ' | '
            print(out)
        print(5*'---------------')#per 3 kolommen 1 keer


class Player:
    def __init__(self, name, exp_rate=1):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value

    def getHash(self, board):
        boardHash = str(board.reshape(BOARD_COLS * BOARD_ROWS))
        return boardHash

    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action

    # append a hash state
    def addState(self, state):
        self.states.append(state)

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.lr * (self.decay_gamma * reward - self.states_value[st])
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'ab')
        pickle.dump(self.states_value, fw)
        print("opgeslagen")
        fw.close()
    def savePolicy_overwrite(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        print("opgeslagen en oversschreven")
        fw.close()

    def loadPolicy(self, file):
        try:
            fr = open(file, 'rb')
            self.states_value = pickle.load(fr)
            fr.close()
        except:
            print("geen policy geladen, bestand?!")


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            col=-1
            row=-1
            while col==-1 or row==-1:#niet gedefinieerd
                try:
                    row = int(input("Input your action row:"))-1
                    col = int(input("Input your action col:"))-1
                except:
                    print("geef een integer")
        
            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass

def thread_trainer():
        global State, Player, overwrite
        
        
        p1 = Player("p1")
        p2 = Player("p2")
        st = State(p1, p2)
        if overwrite==True:
            p1.savePolicy_overwrite()#schrijf alle data naar daar met wb
            p2.savePolicy_overwrite()#schrijf alle data naar daar met wb
            print("data van vorige trainingen weggegooid")
        else:
            print("data van vorige training behouden")
        print("training_thread")
        
        st.play(50000)
        p1.savePolicy()
        p2.savePolicy()
        
        #print("thread_training beeindigd.")

if __name__ == "__main__":
    while overwrite=='':
            try:
                invoer=int(input("Geef 1 voor overschrijven en 0 voor behouden vorige data    "))
                if invoer==1:
                    overwrite=True
                elif invoer==0:
                    overwrite=False
                else:
                    continue
            except:
                print("geef een integer")
    # training
    thread_training2=Thread(target=thread_trainer,daemon=True)
    thread_training2.start()
    thread_training3=Thread(target=thread_trainer,daemon=True)
    thread_training3.start()
    thread_training4=Thread(target=thread_trainer,daemon=True)
    thread_training4.start()
    
    
    
    p1 = Player("p1")
    p2 = Player("p2")
    st = State(p1, p2)

    if overwrite==True:
        p1.savePolicy_overwrite()#schrijf alle data naar daar met wb
        p2.savePolicy_overwrite()#schrijf alle data naar daar met wb
        print("data van vorige trainingen weggegooid")
    else:
        print("data van vorige training behouden")
    print("training...")
    
    #st.play(50000)
    #p1.savePolicy()
    #p2.savePolicy()
        
    print("klaar met training")
    # play with human
    p1 = Player("computer", exp_rate=0)
    p1.loadPolicy("policy_p1")

    p2 = HumanPlayer("human")

    st = State(p1, p2)
    st.play2()
    p1.savePolicy()
