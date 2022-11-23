

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *

import random,util,math

class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent
      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update
      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)
      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """
    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)

        "*** YOUR CODE HERE ***"
        self.values = util.Counter()


    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        qvalue = self.values[(state,action)]
        return qvalue


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        "*** YOUR CODE HERE ***"
        # getting all the actions of a state
        actions = self.getLegalActions(state)
        # value for terminal state is zero
        if len(actions) == 0:
          return 0
        else:
          # the value of other states are just max of the qvalues of the state
          value = max([self.getQValue(state,action) for action in actions])
        return value

    def computeActionFromQValues(self, state):
        """
          Compute the best  to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        actions = self.getLegalActions(state)
        stateMaxQValue = self.computeValueFromQValues(state)
        maxAction = []
        if len(actions) == 0:
          return None
        else:
          maxAction = [action for action in actions if self.getQValue(state, action) == stateMaxQValue]
          ## to select the non-seen state over the negative qvalued state
          # if all(i <= 0 for i in maxAction) and any(i == 0 for i in maxAction) :
          #   maxAction = [action for action in actions if self.getQValue(state, action) == 0]
          #other wise just random.choice of the action that has maximum Q-value
          policy = random.choice(maxAction)
        return policy

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        legalActions = self.getLegalActions(state)
        action = None
        "*** YOUR CODE HERE ***"
        # for an epsilon greedy approad
        # we choose random action epsilon times
        # and optimal 1-epsilon time
        if util.flipCoin(self.epsilon) == True:
          action = random.choice(legalActions)
        else:
          action = self.computeActionFromQValues(state)
        return action

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        # temporal update of q-values
        qValueState = self.getQValue(state,action)
        qValueNextState = self.computeValueFromQValues(nextState)
        self.values[(state,action)] = qValueState + self.alpha*(reward + self.discount*(qValueNextState)- qValueState)
        

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05,gamma=0.8,alpha=0.2, numTraining=0, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1
        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.getAction(self,state)
        self.doAction(state,action)
        return action


class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent
       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """
    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        "*** YOUR CODE HERE ***"
        #extracting featues
        featureVector = self.featExtractor.getFeatures(state,action)
        qvalue = 0
        # for every feature that we extracted for the state and action
        # corresponding weight should be extracted to return the qvalue
        # of a state, which is summation(f_i(s,a)*w_i)
        for k in featureVector.keys():
          qvalue = qvalue + self.weights[k] * featureVector[k]
        return qvalue


    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        "*** YOUR CODE HERE ***"
        #overriding the update function
        ## qvalue for current state is obtained from getQvalue method
        ## for nextState it is calculated using the computevalueFromQvalue method
        qValueCurrentState = self.getQValue(state,action)
        feature = self.featExtractor.getFeatures(state,action)
        qValueNextState = self.computeValueFromQValues(nextState)
        difference = (reward + self.discount*(qValueNextState))- qValueCurrentState
        for k in feature.keys():
          self.weights[k] =  self.weights[k] + self.alpha*(difference)*feature[k]
        

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"
            # print type(self.weights)
            # print "keys", (self.weights.keys())
            pass