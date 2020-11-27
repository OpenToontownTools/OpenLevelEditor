from .LevelEditorGlobals import *

#DNA Utility functions (possible class extensions?)
def DNARemoveChildren(dnaObject):
    """ Utility function to delete all the children of a DNANode """
    children = []
    for i in range(dnaObject.getNumChildren()):
        children.append(dnaObject.at(i))
    for child in children:
        dnaObject.remove(child)
        DNASTORE.removeDNAGroup(child)


def DNARemoveChildOfClass(dnaNode, classType, childNum = 0):
    """ Remove the nth object of that type you come across """
    childCount = 0
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            if childCount == childNum:
                dnaNode.remove(child)
                DNASTORE.removeDNAGroup(child)
                return 1
            childCount = childCount + 1
    # None found
    return 0


def DNARemoveAllChildrenOfClass(dnaNode, classType, notFromLoading = True):
    """ Remove the objects of that type """
    children = []
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            children.append(child)
    for child in children:
        dnaNode.remove(child)
        # [gjeon] because in new LE when this function is called during loading
        # we shouldn't remove dna group from the stroage since it's not added at first
        if notFromLoading:
            DNASTORE.removeDNAGroup(child)


def DNAGetChildren(dnaNode, classType = None):
    """ Return the objects of that type """
    children = []
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if ((not classType)
                or DNAClassEqual(child, classType)):
            children.append(child)
    return children


def DNAGetChild(dnaObject, type = DNA_NODE, childNum = 0):
    childCount = 0
    for i in range(dnaObject.getNumChildren()):
        child = dnaObject.at(i)
        if DNAClassEqual(child, type):
            if childCount == childNum:
                return child
            childCount = childCount + 1
    # Not found
    return None


def DNAGetChildRecursive(dnaObject, type = DNA_NODE, childNum = 0):
    childCount = 0
    for i in range(dnaObject.getNumChildren()):
        child = dnaObject.at(i)
        if DNAClassEqual(child, type):
            if childCount == childNum:
                return child
            childCount = childCount + 1
        else:
            child = DNAGetChildRecursive(child, type, childNum - childCount)
            if child:
                return child

    # Not found
    return None


def DNAGetChildOfClass(dnaNode, classType):
    for i in range(dnaNode.getNumChildren()):
        child = dnaNode.at(i)
        if DNAClassEqual(child, classType):
            return child
    # Not found
    return None


def DNAGetClassType(dnaObject):
    return dnaObject.__class__.getClassType()


def DNAClassEqual(dnaObject, classType):
    return DNAGetClassType(dnaObject) == (classType)


def DNAIsDerivedFrom(dnaObject, classType):
    return DNAGetClassType(dnaObject).isDerivedFrom(classType)


def DNAGetWallHeights(aDNAFlatBuilding):
    """ Get a list of wall heights for a given flat building """
    # Init variables
    heightList = []
    offsetList = []
    offset = 0.0
    # Compute wall heights
    for i in range(aDNAFlatBuilding.getNumChildren()):
        child = aDNAFlatBuilding.at(i)
        if DNAClassEqual(child, DNA_WALL):
            height = child.getHeight()
            heightList.append(height)
            offsetList.append(offset)
            offset = offset + height
    return heightList, offsetList


def DNAGetBaselineString(baseline):
    s = ""
    for i in range(baseline.getNumChildren()):
        child = baseline.at(i)
        if DNAClassEqual(child, DNA_SIGN_TEXT):
            s = s + child.getLetters()
        elif DNAClassEqual(child, DNA_SIGN_GRAPHIC):
            s = s + '[' + child.getCode() + ']'
    return s


def DNASetBaselineString(baseline, text):
    # TODO: Instead of removing all the text and replacing it,
    # replace each text item and then add or remove at the end.
    # This should allow inlined graphics to stay in place.
    # end of todo.
    DNARemoveAllChildrenOfClass(baseline, DNA_SIGN_TEXT)

    # We can't just blindly iterate through the text, because it might
    # be utf-8 encoded, meaning some characters are represented using
    # multi-byte sequences.  Instead, create a TextNode and use it to
    # iterate through the characters of the text.
    t = TextNode('')
    t.setText(text)
    for i in range(t.getNumChars()):
        ch = t.getEncodedChar(i)
        text = DNASignText("text")
        text.setLetters(ch)
        baseline.add(text)


def importModule(dcImports, moduleName, importSymbols):
    """
    Imports the indicated moduleName and all of its symbols
    into the current namespace.  This more-or-less reimplements
    the Python import command.
    """

    # RAU copied from $DIRECT/src/distributed/ConnectionRepository
    module = __import__(moduleName, globals(), locals(), importSymbols)

    if importSymbols:
        # "from moduleName import symbolName, symbolName, ..."
        # Copy just the named symbols into the dictionary.
        if importSymbols == ['*']:
            # "from moduleName import *"
            if hasattr(module, "__all__"):
                importSymbols = module.__all__
            else:
                importSymbols = list(module.__dict__.keys())

        for symbolName in importSymbols:
            if hasattr(module, symbolName):
                dcImports[symbolName] = getattr(module, symbolName)
            else:
                raise Exception('Symbol %s not defined in module %s.' % (symbolName, moduleName))
    else:
        # "import moduleName"

        # Copy the root module name into the dictionary.

        # Follow the dotted chain down to the actual module.
        components = moduleName.split('.')
        dcImports[components[0]] = module
