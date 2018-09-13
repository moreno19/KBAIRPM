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
    '''
    possible (existing verbal) attributes:

    shape - "something"
    fill - y/n
    size - huge, very large, large, medium, small

    NOT ALWAYS PRESENT - we want to add these
    angle - [0,360)
    alignment - "bottom-right"
    inside - a, b, c, etc.
    above - a, b, c, etc.
    '''
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


    #used to figure out which shape from box1 to box2 is most likely corresponding
    #returns dict of mappings: {'a':'c'}
    def matchShapes(self, box1, box2):
        matches = dict()

        self.populateAttributes(box1)
        self.populateAttributes(box2)

        box2list = list(box2)
        

        # TODO - if it finds a higher match later on, go back and correct previous matchings 
        # if there's nothing let, mark as disappeared (#11)
        for shape1 in box1:
            similarities = []

            for shape2 in box2list:

                similarities.append( 
                    self.compareDicts(
                        box1[shape1].attributes, 
                        box2[shape2].attributes
                    )
                )

            # get d2 with most similarities to d1 and pair them
            print similarities
            i = similarities.index(max(similarities))
            print(str(i))
            print box2list[i]
            matches[shape1] = box2list[i]
        
        print matches
            



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


            self.matchShapes(box1_shapes, box2_shapes)
            '''
            get the attribute maps for "corresponding" shapes
            closest set (least differences) is defined as corresponding
            
            map the differences, i.e. the transformation, and save it
            '''

            

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