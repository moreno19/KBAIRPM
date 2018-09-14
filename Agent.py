# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
import numpy


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    #add missing attributes to be able to compare (mostly for VERBAL)
    def populateAttributes(self, box):
        for shape in box:
            if 'angle' not in box[shape].attributes:
                box[shape].attributes['angle'] = ''
            if 'alignment' not in box[shape].attributes:
                box[shape].attributes['alignment'] = ''
            if 'inside' not in box[shape].attributes:
                box[shape].attributes['inside'] = ''
            if 'above' not in box[shape].attributes:
                box[shape].attributes['above'] = ''
            

    # we must be careful in pronunciation  
    # returns an integer counting how many pairs in the dict remain the same      
    def compareDicts(self, d1, d2):
        return len([k for k in d1.keys() if d1.get(k) == d2.get(k)])

    #get key, given dict value - not very optimal, but useful
    def getKey(self, d, val):
        for k, v in d.items():
            if v == val:
                return k

    # runs matchShapes logic again, but only on shapes that have not been used yet
    # Used to recalculate when a more relevant matching shape is found (between figure 1 and 2, for example)
    def reevaluateMatch(self, used, allshapes, currentShape, box1, box2):
        notUsed = list(set(allshapes) - set(used))

        similar = []
        for shape2 in notUsed:
            relevancy = self.compareDicts(
                                box1[currentShape].attributes, 
                                box2[shape2].attributes
                        )   
            similar.append(relevancy)
        
        i = similar.index(max(similar)) #index of most relevant candidate shape
        return allshapes[i]
        


    #used to figure out which shape from box1 to box2 is most likely corresponding
    #returns dict of mappings: {'a':'c'}
    def matchShapes(self, box1, box2):

        # matching shapes stored as pairs
        # this is possibly modified after comparing new shapes, as more relevant ones could be found
        # this is returned 
        matches = dict() 

        # keeps track of shapes already used.
        # If a used shape is found to be the most relevant, check its relevancy score
            # Relevance: 0 - 7 (7 being identical to pretransformation shape)
        # { 'b': 7 }
        used = dict()

        # convert to list so we can track the shape at certain index
        box2list = list(box2) 

        self.populateAttributes(box1)
        self.populateAttributes(box2)

        for shape1 in box1:
            similarities = []

            for shape2 in box2list:

                relevancy = self.compareDicts(
                                box1[shape1].attributes, 
                                box2[shape2].attributes
                            )

                similarities.append( relevancy )

            #get the most similar shape of the ones we saw
            r = max(similarities) #relevancy
            i = similarities.index(max(similarities)) #index of most relevant candidate shape
            candidate = box2list[i] 

  
            if candidate in used.keys():
                if used.get(candidate) < r: # if new relevancy is higher, replace and go with new one
                    
                    #update used dict
                    used[candidate] = r

                    #update previous keys in matches
                    k = self.getKey(matches, candidate)
                    matches[k] = self.reevaluateMatch(list(used), box2list, shape1, box1, box2)

                    #set current matches key to new shape
                    matches[shape1] = candidate

                    
         
            #new shape, match it up!
            else:
                # example: { 'b': 6, 'd': 4}
                used[candidate] = r
                matches[shape1] = candidate
        
        print matches
        return matches
            

    # returns the amount of deletions based on the number of shapes
    # returns 0 if no deletions
    def deleteCheck(self, box1, box2):
        return abs( len(box1) - len(box2) )

    # get shapes (they are matched now), 
    # compare attribute changes between figure 1 and figure 2
    # return transformation dictionary
    '''
    possible (existing verbal) attributes:

    angle - [0,360)
    inside - a, b, c, etc.
    shape - "something"
    above - a, b, c, etc.
    size - huge, very large, large, medium, small
    alignment - "bottom-right"
    fill - y/n and bottom, top, left, right
    
    '''
    def getTransformations(self, box1, box2, matches):
        transformlist = []

        for shape1, shape2 in matches.items():
            transformations = dict()
            a1 = box1[shape1].attributes
            a2 = box2[shape2].attributes

            #if EXACTLY the same, set empty string for this match - no transformation
            if self.compareDicts(a1, a2) == len(a1): 
                transformlist.append('nochange')
                break

            #angle - no change is 0
            if a2['angle'] and a1['angle']:
                transformations['angle'] = int( a2['angle'] ) - int( a1['angle'] )
            else:
                transformations['angle'] = 0

            #shape
            if a1['shape'] != a2['shape']:
                transformations['shape'] = [ a1['shape'], a2['shape'] ]
            else:
                transformations['shape'] = None

            #above
            if a1['above'] != a2['above']:
                transformations['above'] = [ a1['above'], a2['above'] ]
            else:
                transformations['above'] = None

            #TODO - right half, left half, top half, bottom half
            #fill
            if a1['fill'] == 'no' and a2['fill'] == 'yes':
                transformations['fill'] = 'shadein'
            elif a1['fill'] == 'yes' and a2['fill'] == 'no':
                transformations['fill'] = 'deleteshade'
            else:
                transformations['fill'] = None

            #alignment - TODO use centers of shape to track movement. For now will only be verbal
            if a1['alignment'] != a2['alignment']:
                transformations['alignment'] = [ a1['alignment'], a2['alignment'] ]
            else:
                transformations['alignment'] = None

            #size - small, medium, large, very large, huge
            sizes = {'small':1, 'medium':2, 'large':3, 'very large':4, 'huge':5 }
            a1size = a1['size']
            a2size = a2['size']

            if a1size != a2size: #shrinking and growing
                transformations['size'] = (sizes[a2size] - sizes[a1size])
            else:
                transformations['size'] = None

            #inside
            #this one needs some more thought

            transformlist.append(transformations)
        return transformlist

        #TODO deal with deletions






    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self,problem):
        if problem.problemType == "2x2":

            #get the existing 3 boxes (aka figures)
            box1 = problem.figures["A"]
            box2 = problem.figures["B"]
            box3 = problem.figures["C"]

            #get the objects from each box and store them in a set
            box1_shapes = box1.objects
            box2_shapes = box2.objects
            box3_shapes = box3.objects

            #match up corresponding shapes between transformations
            matches = self.matchShapes(box1_shapes, box2_shapes)
            
            #get number of deletes
            deletes = self.deleteCheck(box1_shapes, box2_shapes)
            
            #get transformations
            transformations = self.getTransformations(box1_shapes, box2_shapes, matches)
            print 'transformations:'
            print transformations

            print problem.name + " ---- box 1"
            for shape in box1_shapes:
                print box1_shapes[shape].name
                print box1_shapes[shape].attributes
                
            print '\n'
            print problem.name + " ---- box 2"
            for shape in box2_shapes:
                print box2_shapes[shape].name
                print box2_shapes[shape].attributes
            print '\n'
            print '\n'


        else:
            pass

        return -1