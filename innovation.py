from connectionGene import connectionGene
from nodeGene import nodeGene
import random as rand
# TODO: this is so inherent to creating connections it should be in the connectionGene constructor!
#               ConnectionGene construction is becoming spaghetti in higher order objects. Fix this.
# TODO: is it simpler to just pass in list of all existing connections to connectionGene and check in constructor?


class globalConnections:
    # TODO: refactor name since more than connections 'globalMaps'?
    '''
    keep a record of all global variables that define the fitness landscape mapping
    '''

    def __init__(self):
        self.connections = []
        self.innovation = 0
        self.nodeId = 0  # This should be held here since global variable

    #called in addConnection
    def verifyConnection(self, verifyConnection):
        '''
        Parameters:
            verifyConnection: takes in a connection without innovation assigned to be checked against global list.
        Returns:
            connection: either the new connection or a connection that is identical.
        '''
        # check all connections for matching input and output
        # TODO: find a way to lambda function transform list and search for max more efficiently than iteration
        for connection in self.connections:
            if verifyConnection.input.nodeId == connection.input.nodeId and verifyConnection.output.nodeId == connection.output.nodeId:
                # if verifyConnection.innovation == connection.innovation:
                copyConnection = connectionGene.copy_from(verifyConnection)
                del verifyConnection
                return copyConnection

        self.connections.append(verifyConnection)
        self.innovation += 1
        # TODO: does this assign int object instance or value? *sigh* just high level things
        verifyConnection.innovation = self.innovation
        return verifyConnection

    def verifyNode(self, input, output):
        '''
        check to see if a newly split connection has already occured
        '''
        self.nodeId += 1
        newNode = nodeGene(self.nodeId)
        inConnection = connectionGene(rand.uniform(-1, 1), input, newNode)
        outConnection = connectionGene(rand.uniform(-1, 1), output, newNode)

        for connection in self.connections:
            if inConnection.input.nodeId == connection:
                firstMatch = connection
                check = inConnection.output.nodeId
                for secondConnection in (self.connections - inConnection):
                    if outConnection.output.nodeId == secondConnection.output.nodeId and outConnection.input.nodeId == check:
                        # undo the created connections and return new objects of the matches
                        del inConnection, outConnection
                        connectionGene.copy_from(firstMatch)
                        connectionGene.copy_from(secondConnection)
                        return newNode
        # novel node acquired
        self.innovation += 1
        inConnection.innovation = self.innovation
        self.innovation += 1
        outConnection.innovation = self.innovation
        return newNode

        # return connectionGene.copy_from(firstMatch), connectionGene.copy_from(secondConnection)
        # return inConnection, outConnection

        # @DEPRECATED
        # def update(self, connections):
        #     '''
        #     update the list of global connections without verification
        #     Parameters:
        #         connections or connection to be added to global list
        #     Returns:
        #         None
        #     '''
        #     if isinstance(connections, list):
        #         self.connections.extend(connections)
        #         self.innovation += len(connections)  # TODO: ?
        #     else:  # is one connection
        #         self.connections.append(connections)
        #         self.innovation += 1
