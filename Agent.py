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

                #reset
                if 'angle' not in box[shape].attributes:
                    box[shape].attributes['angle'] = 0
                if 'alignment' not in box[shape].attributes:
                    box[shape].attributes['alignment'] = ''
                if 'inside' not in box[shape].attributes:
                    box[shape].attributes['inside'] = 0
                if 'above' not in box[shape].attributes:
                    box[shape].attributes['above'] = 0
                if 'overlaps' in box[shape].attributes:
                    box[shape].pop('overlaps')

                #split up and count ('m,d,g' becomes 3)
                if 'above' in box[shape].attributes and isinstance(box[shape].attributes.get('above'), str):
                    box[shape].attributes['above'] = len( box[shape].attributes.get('above').split(',') )
                if 'inside' in box[shape].attributes and isinstance(box[shape].attributes.get('inside'), str):
                    box[shape].attributes['inside'] = len( box[shape].attributes.get('inside').split(',') )

                #change type
                if 'angle' in box[shape].attributes and isinstance(box[shape].attributes.get('angle'), str):
                    box[shape].attributes['angle'] = int(box[shape].attributes.get('angle'))
            except:

                #reset
                if 'angle' not in box[shape]:
                    box[shape]['angle'] = 0
                if 'alignment' not in box[shape]:
                    box[shape]['alignment'] = ''
                if 'inside' not in box[shape]:
                    box[shape]['inside'] = 0
                if 'above' not in box[shape]:
                    box[shape]['above'] = 0
                if 'overlaps' in box[shape]:
                    box[shape].pop('overlaps')

                #split up and count ("a,b,c" becomes 3)
                if 'above' in box[shape] and isinstance(box[shape].get('above'), str):
                    box[shape]['above'] = len ( box[shape].get('above').split(','))
                if 'inside' in box[shape] and isinstance(box[shape].get('inside'), str):
                    box[shape]['inside'] = len ( box[shape].get('inside').split(','))
                
                #change type
                if 'angle' in box[shape] and isinstance(box[shape].get('angle'), str):
                    box[shape]['angle'] = int( box[shape].get('angle'))

        return box
            

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
            try:
                relevancy = self.compareDicts(
                                    box1[currentShape].attributes, 
                                    box2[shape2].attributes
                            )   
            except:
                relevancy = self.compareDicts(
                                    box1[currentShape],
                                    box2[shape2]
                            )
            similar.append(relevancy)


        if similar != []:
            i = similar.index(max(similar)) #index of most relevant candidate shape
        else:
            return None

        return allshapes[i]
        
    def preTransformCheck(self, box1, box3):
        # If onethree is true, check if boxes one and three are identical. If they are, then
        # answer for b4 is same as b2
        box1 = self.populateAttributes(box1)
        box3 = self.populateAttributes(box3)

        attributes1 = []
        attributes3 = []

        for shape in box1.values():

            #split 'inside', since we skipped the transformation
            if shape.attributes['inside'] == '':
                shape.attributes['inside'] = 0
            elif not isinstance( shape.attributes['inside'], int):
                shape.attributes['inside'] = len( shape.attributes.get('inside').split(',') )
            attributes1.append(shape.attributes)
        
        for shape in box3.values():

            #split 'inside', since we skipped the transformation
            if shape.attributes['inside'] == '':
                shape.attributes['inside'] = 0
            elif not isinstance( shape.attributes['inside'], int):
                shape.attributes['inside'] = len( shape.attributes.get('inside').split(',') )
            attributes3.append(shape.attributes)

        if attributes1 == attributes3:
            return True
        else:
            return False


    #used to figure out which shape from box1 to box2 is most likely corresponding
    #returns dict of mappings: {'a':'c'}
    # onethree is used for cases when b1 and b3 are identical, then we can argue that
    # 2 and 4 will be identical and skip the process
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

        box1 = self.populateAttributes(box1)
        box2 = self.populateAttributes(box2)

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
                    
                    temp = self.reevaluateMatch(list(used), box2list, shape1, box1, box2)
                    if temp != None:
                        matches[k] = temp
                    else:
                        del matches[k]
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
            

    def sizeToString(self, a):
        if a == 1:
            return 'very small'
        elif a == 2:
            return 'small'
        elif a == 3:
            return 'medium'
        elif a == 4:
            return 'large'
        elif a == 5:
            return 'very large'
        elif a == 6:
            return 'huge'
        else:
            return a



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

            a1size = self.sizeToString(a1size)
            a2size = self.sizeToString(a2size)

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

            if transformations['angle'] == 0 and transformations['inside'] == 0 and transformations['shape'] == '' and transformations['above'] == 0 and transformations['size'] == 0 and transformations['alignment'] == '' and transformations['fill'] == '':
                transformations = "nochange"

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
    def modifyAttributes(self, trans, shapeAtts, shape, deleted, box1, box2, box3):
        box1 = [v.attributes for k,v in box1.items()]
        box2 = [v.attributes for k,v in box2.items()]
        box3 = [v.attributes for k,v in box3.items()]

        newshape = {'inside': 0, 'above': 0, 'shape': '', 'fill': '', 'angle': 0, 'size': '', 'alignment': ''}
        
        if trans == 'nochange':
            return shapeAtts
        elif trans == 'deleted':
            return 'deleted'
        else:
            
            #special case
            corners = [45, 135, 225, 315]
            if int(box1[0].get('angle')) in corners:
                corners.remove(int(box1[0].get('angle')))
            if int(box2[0].get('angle')) in corners:
                corners.remove(int(box2[0].get('angle')))
            if int(box3[0].get('angle')) in corners:
                corners.remove(int(box3[0].get('angle')))
            if len(corners) == 1:
                newshape['angle'] = corners[0]
            elif trans.get('angle') == '':
                newshape['angle'] = shapeAtts.get('angle')
            
            '''
            newshape['angle'] = (int(shapeAtts['angle']) - int(trans['angle']))
            if newshape.get('angle') > 360:
                newshape['angle'] = newshape.get('angle') % 360
            if newshape.get('angle') < 360:
                newshape['angle'] = (newshape.get('angle') + 360) % 360
            if newshape.get('angle') == 360:
                newshape['angle'] = 0
            # TODO - try rotating both ways
            '''

            if trans.get('shape') == '' or trans.get('shape') == None:
                newshape['shape'] = shapeAtts.get('shape')
            else: 
                if shapeAtts.get('shape') == trans.get('shape')[0]:
                    newshape['shape'] = trans.get('shape')[1]        
            
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

            if trans.get('alignment') == '' or trans.get('alignment') == None:
                newshape['alignment'] = shapeAtts.get('alignment')
            else:
                if shapeAtts.get('alignment') == trans.get('shape')[0]:
                    newshape['alignment'] = trans.get('alignment')[1]

                elif trans.get('alignment')[0] == 'bottom-right' and trans.get('alignment')[1] == 'bottom-left' and shapeAtts.get('alignment') == 'bottom-left':
                    newshape['alignment'] = 'bottom-right'
                elif trans.get('alignment')[0] == 'bottom-left' and trans.get('alignment')[1] == 'bottom-right' and shapeAtts.get('alignment') == 'bottom-right':
                    newshape['alignment'] = 'bottom-left'

                elif trans.get('alignment')[0] == 'top-left' and trans.get('alignment')[1] == 'top-right' and shapeAtts.get('alignment') == 'top-right':
                    newshape['alignment'] = 'top-left'
                elif trans.get('alignment')[0] == 'top-right' and trans.get('alignment')[1] == 'top-left' and shapeAtts.get('alignment') == 'top-left':
                    newshape['alignment'] = 'top-right'

                elif trans.get('alignment')[0] == 'bottom-right' and trans.get('alignment')[1] == 'bottom-left' and shapeAtts.get('alignment') == 'top-right':
                    newshape['alignment'] = 'top-left'
                elif trans.get('alignment')[0] == 'bottom-left' and trans.get('alignment')[1] == 'bottom-right' and shapeAtts.get('alignment') == 'top-left':
                    newshape['alignment'] = 'top-right'

                elif trans.get('alignment')[0] == 'top-left' and trans.get('alignment')[1] == 'top-right' and shapeAtts.get('alignment') == 'bottom-left':
                    newshape['alignment'] = 'bottom-right'
                elif trans.get('alignment')[0] == 'top-right' and trans.get('alignment')[1] == 'top-left' and shapeAtts.get('alignment') == 'bottom-right':
                    newshape['alignment'] = 'bottom-left'

                
            

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
    def transformBox(self, box, mapping, transformations, deleted, created, box1, box2, box3):
        attributes = []
        keys = []

        c = 97 #used to construct dict keys - chr()

        for name, shape3 in box.items():
            if name in mapping.keys():
                shape1 = mapping.get(name) #returns shape1 name
                trans = transformations.get(shape1) #returns transformation dict
                t = self.modifyAttributes(trans, shape3.attributes, name, deleted, box1, box2, box3)
                if t != "deleted":
                    attributes.append(t)
            else:
                # new shapes in box3 that don't match up to any in
                # box 1
                
                attributes.append(shape3.attributes)

        #add any shapes that were created to box4/box4b
        if created:
                for shape in created:
                    attributes.append(shape)

        for a in attributes:
            k = str(chr(c))
            c += 1
            if k not in keys:
                keys.append(k)
            else:
                while str(chr(c)) in keys:
                    c += 1
        

        box4 = dict(zip(keys, attributes))
        return box4
                
    # used only when box1 and box3 are the same
    def box2AsAnswer(self, possibleAnswers, box):
        allScores = []

        for eachAnswer in possibleAnswers:
            answerScore = []
            shapes = []
            t = []

            #setup all attributes in figure in list for comparison
            for v in eachAnswer.objects:
                if isinstance(eachAnswer.objects.get(v).attributes.get('inside'), str):
                    eachAnswer.objects.get(v).attributes['inside'] = len( eachAnswer.objects.get(v).attributes.get('inside').split(',') )
                shapes.append(eachAnswer.objects.get(v).attributes)
            for _, v in box.items():
                if isinstance(v.attributes.get('inside'), str):
                    v.attributes['inside'] = len( v.attributes.get('inside').split(',') )
                t.append(v.attributes)
            box2 = t

            # if they have a different number of shapes, just continue
            # this one won't be the right answer
            if len(shapes) != len(box2):
                answerScore.append(0)
                continue

            # if the have the same number of shapes though:
            # populate missing attributes so we can compare
            for att in shapes:
                if 'angle' not in att:
                    att['angle'] = 0
                if 'inside' not in att:
                    att['inside'] = 0
                if 'above' not in att:
                    att['above'] = 0
                if 'alignment' not in att:
                    att['alignment'] = ''
                if 'overlaps' in att:
                    att.pop('overlaps')

            for att in box2:
                if 'angle' not in att:
                    att['angle'] = 0
                if 'inside' not in att:
                    att['inside'] = 0
                if 'above' not in att:
                    att['above'] = 0
                if 'alignment' not in att:
                    att['alignment'] = ''
                if 'overlaps' in att:
                    att.pop('overlaps')

            #compare the two lists
            # take the average number of similar attributes across
            # all shapes between the two boxes
            shapesimilarityall = []

            shapes.sort()
            box2.sort()
            

            for i in xrange(len(box2)):
                if isinstance(shapes[i].get('angle'), str):
                    shapes[i]['angle'] = int(shapes[i]['angle'])
                shapesimilarity = self.compareDicts(
                                shapes[i],
                                box2[i]
                                )   
                shapesimilarityall.append(shapesimilarity)

            similarity = sum(shapesimilarityall)
            answerScore.append(similarity)
            
            avgscore = sum(answerScore)
            allScores.append(avgscore)

        guess = allScores.index(max(allScores)) + 1
        
        if allScores.count(max(allScores)) > 1:
            return -1
        else:
            return guess

    def processAndGuess(self, possibleAnswers, box4, numdeleted, numcreated): 
        if numdeleted == None:
            numdeleted = 0
        if numcreated == None:
            numcreated = 0
        allScores = []

        for eachAnswer in possibleAnswers:
            answerScore = []

            shapes = self.setupAnswers(eachAnswer)


            if len(shapes) != len(box4) and abs(len(shapes) - len(box4)) != (numcreated - numdeleted):
                allScores.append(0)
                continue
                    

            # get matches (potentialanswer: box4)
            matches, _ = self.matchShapes(shapes, box4)



            # iterate over matches and compare attributes
            for potential, guess in matches.items():
                similarity = self.compareDicts(
                                shapes[potential],
                                box4[guess]
                            )
                answerScore.append(similarity)
            avgscore = sum(answerScore)


            # if the number of shapes don't match up, don't even bother with that choice  
            
            #get average scores of all shapes     
            allScores.append(avgscore)

        guess = allScores.index(max(allScores)) + 1


        '''
        print "multiple choice attributes for chosen answer are:"
        for i in xrange(6):
            for k,v in possibleAnswers[i].objects.items():
                print v.attributes
            print '\n'
        '''
        
        return guess, allScores

    # used to get answers and extract their shapes
    def getAnswers(self, possibleAnswers, box4, deleted13, mapping13, mapping12, box1, box3, box2):
        #prework
        numdeleted = len(deleted13)
        
        #process and guess
        guess, allScores = self.processAndGuess(possibleAnswers, box4, None, None)

        # IF THERE STILL ISN'T A CLEAR ANSWER, run vertical comparison: 
        # 1 to 3 transformation, instead of just 1 to 2
        if allScores.count(max(allScores)) > 1:

            #store all potential answers if there is more than 1
            potentialAnswers = []

            '''
            print "possible solutions that tied:"
            m = max(allScores)
            for i in xrange(len(allScores)):
                if allScores[i] == m:
                    print i + 1
            allScores1 = allScores     
            print allScores1    
            '''

            #now run the algorithm again, but vertically instead of horizontally        
            
            #reverse mapping13, because it's actually mapping31
            mapping13 = {v:k for k, v in mapping13.items()}

            #check for appending shapes
            # TODO currently NAIVE implementation: +3 deletions and +2 additions
            # will be the same as 1 deletion, which is incorrect, but might still work
            # for basic problems
            created13 = []
            box1_shapes = [v.attributes for k,v in box1.items()]
            box3_mapped = [v for k, v in mapping13.items()]

            for name, att in box3.items():
                if name not in box3_mapped:
                    created13.append(att.attributes)
            numcreated = len(created13)

            #matches between 1 and 3 already setup: mapping13
            #get transform between 1 and 3:
            transform13 = self.getTransformations(box1, box3, mapping13, deleted13)


            #now, transform box2 into "box4 - b", which will get fused with the original box4 after
            mapping12 = {v:k for k, v in mapping12.items()}
            box4B = self.transformBox(box2, mapping12, transform13, deleted13, created13, box1, box2, box3)

            guess, allScores = self.processAndGuess(possibleAnswers, box4B, numdeleted, numcreated)

        if allScores.count(max(allScores)) == 1:
            return guess
        else:
            newScores = []
            for i in xrange(len(allScores)):
                newScores.append( allScores1[i] + allScores[i])
            guess = newScores.index(max(newScores)) + 1
            
            if newScores.count(max(allScores)) == 1:
                return guess
            else:
                return -1

    def setupAnswers(self, figure):
        a = dict()
        for k, v in figure.objects.items(): 
            a[k] = v.attributes
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


            # match up corresponding shapes between transformations
            matches12, deleted12 = self.matchShapes(box1_shapes, box2_shapes)
            
            # used to check possible answers
            # for example, if numdeleted is none, then number of shapes in 
            # both box3 and the prediction should be the same
            
  
            
            #get transformations
            transformations = self.getTransformations(box1_shapes, box2_shapes, matches12, deleted12)
            


            # Before we bother mapping shapes and transforming, check if boxes 1 and 3 are identical
            # If so, then 2 and 4 will be identical
            identical = self.preTransformCheck(box3_shapes, box1_shapes)

            if not identical:
                # get third box, and match up all the shapes to shapes in box 1
                # we can't start the transformation process without doing this first
                mapping13, deleted13 = self.matchShapes(box3_shapes, box1_shapes)
                
                # apply transformations to box3 to get box4
                # will need to pass more residual information when 'trying'
                # different rotations, shape possibilities, etc.
                box4 = self.transformBox( box3_shapes, mapping13, transformations, deleted12, None, box1_shapes, box2_shapes, box3_shapes)


                #check box 4 against all answers!
                guess = self.getAnswers(possibleAnswers, box4, deleted12, mapping13, matches12, box1_shapes, box3_shapes, box2_shapes)


                
            else: #1 and 3 identical, just get box 2
                guess = self.box2AsAnswer(possibleAnswers, box2_shapes)  

            return guess