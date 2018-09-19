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
from RavensObject import RavensObject


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
            try:
                if 'angle' not in box[shape].attributes:
                    box[shape].attributes['angle'] = 0
                if 'alignment' not in box[shape].attributes:
                    box[shape].attributes['alignment'] = ''
                if 'inside' not in box[shape].attributes:
                    box[shape].attributes['inside'] = 0
                if 'above' not in box[shape].attributes:
                    box[shape].attributes['above'] = 0
            except:
                if 'angle' not in box[shape]:
                    box[shape]['angle'] = 0
                if 'alignment' not in box[shape]:
                    box[shape]['alignment'] = ''
                if 'inside' not in box[shape]:
                    box[shape]['inside'] = 0
                if 'above' not in box[shape]:
                    box[shape]['above'] = 0
            

    # we must be careful in pronunciation  
    # returns an integer counting how many pairs in the dict remain the same      
    def compareDicts(self, d1, d2):
        return len([k for k in d1.keys() if d1.get(k) == d2.get(k)])

    #get key, given dict value - not very optimal, but useful
    def getKey(self, d, val):
        for k, v in d.items():
            if v == val:
                return k

    # helper function for matchShapes
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
        if isinstance(box2, dict):
            box2list = list(box2) 
        else:
            box2list = box2

        self.populateAttributes(box1)
        self.populateAttributes(box2)

        for shape1 in box1:
            similarities = []

            for shape2 in box2list:

                try:
                    relevancy = self.compareDicts(
                                    box1[shape1].attributes, 
                                    box2[shape2].attributes
                                )
                except:
                    relevancy = self.compareDicts(
                                    box1[shape1], 
                                    box2[shape2]
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
        
        
        # at the very end, check for any box1 shapes that didn't get matched up.
        # these were deleted - we need to mark them as such
        deleted = []
        for shape in box1:
            if shape not in matches.keys():
                deleted.append(shape)

        return matches, deleted
            

    


    # get shapes (they are matched now), 
    # compare attribute changes between figure 1 and figure 2
    # return transformation dictionary, (box1 shape : attributes dict)
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
    def getTransformations(self, box1, box2, matches, deleted):
        allTransforms = dict()
        
        for shape1, shape2 in matches.items():
            transformations = dict()
            a1 = box1[shape1].attributes
            a2 = box2[shape2].attributes

            #add all the deleted shapes
            for each in deleted:
                allTransforms[each] = 'deleted'


            #if EXACTLY the same, set nochange string for this match - no transformation
            if self.compareDicts(a1, a2) == len(a1): 
                allTransforms[shape1] = 'nochange'
                continue #not break LOL

            #angle - no change is 0
            if a1['angle'] == '': a1['angle'] = 0
            if a2['angle'] == '': a2['angle'] = 0

            if a2['angle'] and a1['angle']:
                transformations['angle'] = int( a2['angle'] ) - int( a1['angle'] )
            else:
                transformations['angle'] = 0

            #shape
            if a1['shape'] != a2['shape']:
                transformations['shape'] = [ a1['shape'], a2['shape'] ]
            else:
                transformations['shape'] = ''

            #above
            if a1['above'] != a2['above']:
                a1aboveCount = len( (a1['above']).split(',') )
                a2aboveCount = len( (a2['above']).split(',') )

                transformations['above'] = a2aboveCount - a1aboveCount
            else:
                transformations['above'] = 0

            #fill
            if a1['fill'] == 'no' and a2['fill'] == 'yes':
                transformations['fill'] = 'shadein'
            elif a1['fill'] == 'yes' and a2['fill'] == 'no':
                transformations['fill'] = 'deleteshade'
            elif (a1['fill'] == 'right-half' and a2['fill'] == 'left-half') or (a1['fill'] == 'left-half' and a2['fill'] == 'right-half'):
                transformations['fill'] = 'left-right'
            elif (a1['fill'] == 'top-half' and a2['fill'] == 'bottom-half') or (a1['fill'] == 'bottom-half' and a2['fill'] == 'top-half'):
                transformations['fill'] = 'top-down'
            else:
                transformations['fill'] = ''

            #alignment - TODO use centers of shape to track movement. For now will only be verbal
            if a1['alignment'] != a2['alignment']:
                transformations['alignment'] = [ a1['alignment'], a2['alignment'] ]
            else:
                transformations['alignment'] = ''

            #size - very small, small, medium, large, very large, huge
            sizes = {'very small':1, 'small':2, 'medium':3, 'large':4, 'very large':5, 'huge':6 }
            a1size = a1['size']
            a2size = a2['size']

            if a1size != a2size: #shrinking and growing
                transformations['size'] = (sizes[a2size] - sizes[a1size])
            else:
                transformations['size'] = 0

            #inside - count how many it's inside of
            if a1['inside'] != a2['inside']:
                a1aboveCount = len( (a1['inside']).split(',') )
                a2aboveCount = len( (a2['inside']).split(',') )

                transformations['inside'] = a2aboveCount - a1aboveCount
            else:
                transformations['inside'] = 0
            
            
            allTransforms[shape1] = transformations
        return allTransforms



    # Convert shape, inside, and above to numbers
    # helper for modifyAttributes()
    def checkConvert(self, attribute, aType):
        if not isinstance(attribute, int):
            if aType is 'size':
                if attribute == 'very small': attribute = 1
                elif attribute == 'small': attribute = 2
                elif attribute == 'medium': attribute = 3
                elif attribute == 'large': attribute = 4
                elif attribute == 'very large': attribute = 5
                elif attribute == 'huge': attribute = 6
                return attribute
            elif aType is 'inside' or aType is 'above':
                return len(attribute.split(','))
        else:
            return attribute

    # convert shape number to shape string
    # helper for modifyattributes()
    def convert_sizenum_to_sizestring(self, num):
        if num is 1:
            return 'very small'
        if num is 2:
            return 'small'
        if num is 3:
            return 'medium'
        if num is 4:
            return 'large'
        if num is 5:
            return 'very large'
        if num is 6:
            return 'huge'

    # helper for transformBox()
    def modifyAttributes(self, trans, shapeAtts, shape, deleted):
        newshape = {'inside': 0, 'above': 0, 'shape': '', 'fill': '', 'angle': 0, 'size': '', 'alignment': ''}
        
        if trans == 'nochange':
            return shapeAtts
        elif trans == 'deleted':
            pass
        else:
            
            newshape['angle'] = (int(shapeAtts['angle']) + int(trans['angle']))
            if newshape.get('angle') > 360:
                newshape['angle'] = newshape.get('angle') % 360
            # TODO - try rotating both ways

            if trans['shape'] == '' or trans['shape'] == None:
                newshape['shape'] = shapeAtts['shape']
            else: #list of two shapes
                pass
                # TODO get actual shape, delete from list, and try all remaining
                # possible shapes
            
            shapeAtts['above'] = self.checkConvert(shapeAtts['above'], 'above')
            trans['above'] = self.checkConvert(trans['above'], 'above')
            newshape['above'] = int(shapeAtts['above']) + int(trans['above'])
        
            shapeAtts['inside'] = self.checkConvert(shapeAtts['inside'], 'inside')
            trans['inside'] = self.checkConvert(trans['inside'], 'inside')
            newshape['inside'] = int(shapeAtts['inside']) + int(trans['inside'])

            shapeAtts['size'] = self.checkConvert(shapeAtts['size'], 'size')
            trans['size'] = self.checkConvert(trans['size'], 'size')
            newshape['size'] = int(shapeAtts['size']) + int(trans['size'])
            newshape['size'] = self.convert_sizenum_to_sizestring( newshape.get('size') )

            newshape['alignment'] = trans['alignment'] # list with 2 shapes in it

            #fill
            if trans['fill'] == 'shadein':
                newshape['fill'] = 'yes'
            elif trans['fill'] == 'deleteshade':
                newshape['fill'] = 'no'
            elif trans['fill'] == 'left-right' and shapeAtts['fill'] == 'left-half':
                newshape['fill'] = 'right-half'
            elif trans['fill'] == 'left-right' and shapeAtts['fill'] == 'right-half':
                newshape['fill'] = 'left-half'
            elif trans['fill'] == 'top-down' and shapeAtts['fill'] == 'top-half':
                newshape['fill'] = 'bottom-half'
            elif trans['fill'] == 'top-down' and shapeAtts['fill'] == 'bottom-half':
                newshape['fill'] = 'top-half'
            elif trans['fill'] == '' or trans['fill'] == None:
                newshape['fill'] = shapeAtts['fill']
            
        return newshape

    # apply transformation attributes to box 3, to get box4
    # mapping is 3 -> 1, key is shapes from box3, val is shape from box1
    def transformBox(self, box3, mapping, transformations, deleted):
        attributes = []
        keys = []

        c = 97 #used to construct dict keys

        for name, shape3 in box3.items():
            if name in mapping:
                shape1 = mapping.get(name) #returns shape1 name
                trans = transformations.get(shape1) #returns transformation dict
                attributes.append(self.modifyAttributes(trans, shape3.attributes, name, deleted))
            else:
                # new shapes in box3 that don't match up to any in
                # box 1
                
                attributes.append(shape3)

            k = str(chr(c))
            c += 1
            keys.append(k)

        box4 = dict(zip(keys, attributes))
        return box4
                

    # used to get answers and extract their shapes
    def getAnswers(self, possibleAnswers, box):
        allScores = []
    
        for eachAnswer in possibleAnswers:
            answerScore = []

            shapes = self.setupAnswers(eachAnswer)

            # get matches (potentialanswer: box4)
            matches, _ = self.matchShapes(shapes, box)
            
            # iterate over matches and compare attributes
            for potential, guess in matches.items():
                
                similarity = self.compareDicts(
                                shapes[potential],
                                box[guess]
                            )
                answerScore.append(similarity)
            
            avgscore = sum(answerScore) / len(answerScore)
            allScores.append(avgscore)

        guess = allScores.index(max(allScores)) + 1
        
        if allScores.count(max(allScores)) > 1:
            return -1
        else:
            return guess




    def setupAnswers(self, figure):
        a = dict()
        for k, v in figure.objects.items(): 
            a['k'] = v.attributes
        return a





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
        #skip challenge problems for now
        if problem.name.split(' ')[0] == 'Challenge' or problem.problemType != '2x2':
            return -1

        if problem.problemType == "2x2":

            #get the existing 3 boxes (aka figures)
            box1 = problem.figures["A"]
            box2 = problem.figures["B"]
            box3 = problem.figures["C"]

            #get the 6 possible answers for later
            A1 = problem.figures['1']
            A2 = problem.figures['2']
            A3 = problem.figures['3']
            A4 = problem.figures['4']
            A5 = problem.figures['5']
            A6 = problem.figures['6']
            possibleAnswers = [A1, A2, A3, A4, A5, A6]
            
            

            #get the objects from each box and store them in a set
            box1_shapes = box1.objects
            box2_shapes = box2.objects
            box3_shapes = box3.objects


            #match up corresponding shapes between transformations
            matches12, deleted12 = self.matchShapes(box1_shapes, box2_shapes)
        
            
            #get transformations
            transformations = self.getTransformations(box1_shapes, box2_shapes, matches12, deleted12)
            

            # get third box, and match up all the shapes to shapes in box 1
            # we can't start the transformation process without doing this first
            mapping13, _ = self.matchShapes(box3_shapes, box1_shapes)

            # apply transformations to box3 to get box4
            # will need to pass more residual information when 'trying'
            # different rotations, shape possibilities, etc.
            box4 = self.transformBox( box3_shapes, mapping13, transformations, deleted12)
          
            
            
            #check box 4 against all answers!
            guess = self.getAnswers(possibleAnswers, box4)

            print problem.name + " ---- box 1"
            "guess is:"
            print guess

            return guess