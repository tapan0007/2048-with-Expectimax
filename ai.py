from __future__ import absolute_import, division, print_function
import copy, random, math
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1

# Tree node. To be used to construct a game tree. 
class Node: 
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (copy.deepcopy(state[0]), state[1])
        # to store a list of (direction, node) tuples
        self.children = []
        self.player_type = player_type

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        #TODO: complete this
        #Status: Completed
        if len(self.children) == 0:
            return True
        return False

# AI agent. To be used do determine a promising next move.
class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3):
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state) #_(self, init_tile_matrix = None, init_score = 0):

    # recursive function to build a game tree
    def build_tree(self, node=None, depth=0, ec=False):
        if node == None:
            node = self.root
        if depth == self.search_depth:
            return
        if node.player_type == MAX_PLAYER:
            # TODO: find all children resulting from
            for _direction in range(0, 4):
                self.simulator.reset(*(node.state))
                _move = self.simulator.move(_direction)
                if _move == False:
                    continue
                child1 = Node(copy.deepcopy(self.simulator.get_state()), int(not MAX_PLAYER))
                node.children.append((_direction, child1))
                self.build_tree(child1, depth + 1)
            # all possible moves (ignore "no-op" moves)
            # NOTE: the following calls may be useful:
            # self.simulator.reset(*(node.state))
            # self.simulator.get_state()
            # self.simulator.move(direction)
            pass

        elif node.player_type == CHANCE_PLAYER:
            # TODO: find all children resulting from
            open_tiles = self.simulator.get_open_tiles()
            for (i, j) in open_tiles:
                self.simulator.reset(*(node.state))
                self.simulator.tile_matrix[i][j] = 2
                child1 = Node(copy.deepcopy(self.simulator.get_state()), int(not CHANCE_PLAYER))
                node.children.append((-1, child1))
                self.build_tree(child1, depth + 1)
            # all possible placements of '2's
            # NOTE: the following calls may be useful
            # (in addition to those mentioned above):
            # self.simulator.get_open_tiles():
            pass

        # TODO: build a tree for each child of this node

    # expectimax implementation; 
    # returns a (best direction, best value) tuple if node is a MAX_PLAYER
    # and a (None, expected best value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node = None):
        if node == None:
            node = self.root
        if node.is_terminal():
            return (-1, node.state[1])
        elif node.player_type == MAX_PLAYER:
            # TODO: MAX_PLAYER logic
            max_val = 0
            max_dir = -1
            child_nodes = node.children
            for (dir, _child) in child_nodes:
                val_node = self.expectimax(_child)
                if val_node[1] > max_val:
                    max_val = val_node[1]
                    max_dir = dir
            return (max_dir, max_val)

        elif node.player_type == CHANCE_PLAYER:
            # TODO: CHANCE_PLAYER logic
            expected_val = 0
            for (dir, _child) in node.children:
                expected_val = expected_val + ((1.0 / len(node.children)) * self.expectimax(_child)[1])
            return (-1, expected_val)


    '''
    Alternate method of computing score of each terminal state
    '''
    def compute_weighted_score(self, tile_matrix):
        new_metric = 0
        cnt = 15
        empty_tiles = 0
        for i in range(4):
            if i % 2 == 0:
                for j in range(4):
                    if tile_matrix[i][j] == 0: empty_tiles += 1
                    new_metric += ((pow(4, cnt)) * tile_matrix[i][j])
                    cnt -= 1
            else:
                for j in range(3, -1, -1):
                    if tile_matrix[i][j] == 0: empty_tiles += 1
                    new_metric += ((pow(4, cnt)) * tile_matrix[i][j])
                    cnt -= 1
        return new_metric
    '''
    New build function for the expectimax tree
    '''
    def build_tree_improved(self, node=None, depth=0, ec=False):
        if node == None:
            node = self.root
        if depth == self.search_depth:
            return
        if node.player_type == MAX_PLAYER:
            for _direction in range(0, 4):
                self.simulator.reset(*(node.state))
                _move = self.simulator.move(_direction)
                if _move == False:
                    continue
                child1 = (Node(copy.deepcopy(self.simulator.get_state()), int(not MAX_PLAYER)))
                node.children.append((_direction, child1,
                          self.compute_weighted_score(self.simulator.tile_matrix)))
                self.build_tree_improved(child1, depth + 1)
            pass

        elif node.player_type == CHANCE_PLAYER:
            open_tiles = self.simulator.get_open_tiles()
            for (i, j) in open_tiles:
                self.simulator.reset(*(node.state))
                self.simulator.tile_matrix[i][j] = 2
                child1 = Node(copy.deepcopy(self.simulator.get_state()), int(not CHANCE_PLAYER))
                node.children.append((-1, child1, self.compute_weighted_score(self.simulator.tile_matrix)))
                self.build_tree_improved(child1, depth + 1)
            pass
    '''
    Improved Expectimax 
    '''
    def expectimax_improved(self,  new_score, node = None):
        if node == None:
            node = self.root
        if node.is_terminal():
            return (-1, new_score)
        elif node.player_type == MAX_PLAYER:
            # TODO: MAX_PLAYER logic
            max_val = -1e10
            max_dir = -1
            child_nodes = node.children
            for (dir, _child, new_score) in child_nodes:
                val_node = self.expectimax_improved(new_score, _child)
                if val_node[1] > max_val:
                    max_val = val_node[1]
                    max_dir = dir
            return (max_dir, max_val)

        elif node.player_type == CHANCE_PLAYER:
            expected_val = 0
            for (dir, _child, new_score) in node.children:
                expected_val = expected_val + ((1.0 / len(node.children)) * self.expectimax_improved(new_score,_child)[1])
            return (-1, expected_val)

    # Do not modify this function

    def compute_decision(self):
        self.build_tree()
        direction, _ = self.expectimax(self.root)
        return direction

    def compute_decision_ec(self):
        self.build_tree_improved()
        #direction, _ = self.expectimax(self.root)
        direction, _score= self.expectimax_improved(0, self.root)
        return direction
