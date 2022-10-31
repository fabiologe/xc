# -*- coding: utf-8 -*-
''' Functions that are useful when dealing with load combinations.'''

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AO_O)"
__copyright__= "Copyright 2015, LCPT and AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@ciccp.es ana.ortega@ciccp.es"

import math
import sys
import loadCombinations

class CombGenerator(object):
    ''' Base class for load combination generators.

    :ivar controlCombGenerator: C++ object used to compute the combinations.
    :ivar actionsAdnFactors: actions with its factors (partial safety factors and combination factors).
    '''

    def __init__(self, combGeneratorName, factors):
        ''' Constructor.'''
        self.name= combGeneratorName
        self.controlCombGenerator= loadCombinations.LoadCombGenerator()
        self.actionsAndFactors= self.controlCombGenerator.actionWeighting.create(self.name, factors)

    def newAction(self, family: str, actionName: str, actionDescription: str, combinationFactorsName:str, partialSafetyFactorsName:str, dependsOn= None, incompatibleActions= None):
        ''' Creates an action and appends it to the combinations generator.

        :param weighting: name of the weighting factors repository.
        :param family: family to which the action belongs ("permanent", "variable", "seismic",...)
        :param actionName: name of the action.
        :param actionDescription: description of the action.
        :param combinationFactorsName: name of the combination factors container.
        :param partialSafetyFactorsName: name of the partial safety factor container.
        :param dependsOn: name of another load that must be present with this one (for example brake loads depend on traffic loads).
        :param incompatibleActions: list of regular expressions that match the names of the actions that are incompatible with this one.
        '''
        newAction= loadCombinations.Action(actionName, actionDescription)
        retval= self.controlCombGenerator.insert(self.name, family, newAction, combinationFactorsName, partialSafetyFactorsName)
        if(dependsOn is not None):
            retval.getRelaciones.appendMain(dependsOn)
        if(incompatibleActions is not None):
            for actionNameRegex in incompatibleActions:
                retval.getRelaciones.appendIncompatible(actionNameRegex)
        return retval

    def computeCombinations(self):
        ''' Compute the load combinations.'''
        self.controlCombGenerator.genera()

    def getLoadCombinations(self):
        ''' Return a container with the computed load combinations.'''
        return self.controlCombGenerator.getLoadCombinations

    def getSLSCharacteristicCombinations(self):
        ''' Return the characteristic combinations for the serviceability limit 
            states.
        '''
        return self.getLoadCombinations().getSLSCharacteristicCombinations
    
    def getSLSFrequentCombinations(self):
        ''' Return the frequent combinations for the serviceability limit 
            states.
        '''
        return self.getLoadCombinations().getSLSFrequentCombinations

    def getSLSQuasiPermanentCombinations(self):
        ''' Return the quasi-permanent combinations for the serviceability
            limit states.
        '''
        return self.getLoadCombinations().getSLSQuasiPermanentCombinations

    def getULSTransientCombinations(self):
        ''' Return the combinations for permanent and transient situations 
            corresponding to ultimate limit states.
        '''
        return self.getLoadCombinations().getULSTransientCombinations

    def getULSAccidentalCombinations(self):
        ''' Return the combinations for accidental situations corresponding
            to ultimate limit states.
        '''
        return self.getLoadCombinations().getULSAccidentalCombinations
    
    def getULSSeismicCombinations(self):
        ''' Return the combinations for seismic situations corresponding
            to ultimate limit states.
        '''
        return self.getLoadCombinations().getULSSeismicCombinations

def getCombinationDict(loadCombination:str):
    ''' Return a Python dictionary whose keys are the names of the actions
        in the combination and whose values are the factor that multiply the
        action.

    :param loadCombination: string of the form "1.00*G1 + 1.00*G2 + 1.35*Qwind"
    '''
    retval= dict()
    if(len(loadCombination)>0):
        loads= loadCombination.split('+')
        for l in loads:
            l= l.strip()
            factor, action= l.split('*')
            retval[action]= float(factor)
    return retval

def getCombinationExpr(combDict:dict):
    ''' Return the expression corresponding to the load combination argument
        in dictionary form (i. e.: {'G1':1.0, 'G2':1.00, 'Qwind':1.35}).

    :param combDict: combination expressed in the form of a dictionary.
    '''
    tmp= list()
    for key in combDict:
        factor= combDict[key]
        tmp.append(str(factor)+'*'+key)
    retval= ''
    if(len(tmp)>0):
        retval= tmp[0]
        for s in tmp[1:]:
            retval+='+'+s
    return retval
    
def splitCombination(loadCombination:str, loads):
    ''' Return the part of a combination that concerns the actions passed as
        argument and then the rest of the original combination.

    :param loads: names of the desired loads.
    '''
    combDict= getCombinationDict(loadCombination)
    tmp1= list(); tmp2= list()
    for key in combDict:
        factor= combDict[key]
        addend= str(factor)+'*'+key
        if(key in loads):
            tmp1.append(addend)
        else:
            tmp2.append(addend)
    retval= '+'.join(tmp1), '+'.join(tmp2)
    return retval

def getFileNameFromCombinationExpresion(loadCombination:str):
    ''' Return a valid filename from the combination expression.'''
    return ''.join(x for x in loadCombination if x.isalnum())

def listActionGroup(actionGroup):
    '''List the defined actions in a group (permanent, variable, accidental).'''
    for familyName in actionGroup.getKeys():
        print('    actions family: ', familyName)
        actionFamily= actionGroup[familyName]
        print('      partial safety factors: ', actionFamily.partial_safety_factors)
        for a in actionFamily.actions:
          print('     ', a)

def listActionFamily(actionFamily):
    '''List the defined actions in a family.

    :param actionFamily: family of actions. 
    '''
    print('    partial safety factors: ', actionFamily.partial_safety_factors)
    actions= actionFamily.actions
    for a in actions:
        print('     ', a)

def listActionWeighting(actionWeighting):
    '''List the defined actions and the weighting for each one.'''
    for awKey in actionWeighting.getKeys():
        print(awKey)
        aw= actionWeighting[awKey]
        print('  Permanent actions: ')
        listActionGroup(aw.permanentActions)
        print('  Non-constant permanent actions: ')
        listActionGroup(aw.ncPermanentActions)
        print('  Variable actions: ')
        listActionGroup(aw.variableActions)
        print('  Accidental actions: ')
        listActionFamily(aw.accidentalActions)
        print('  Seismic actions: ')
        listActionFamily(aw.seismicActions)

def getNamedCombinations(loadCombinations, prefix):
    '''Return a dictionary containing the load combinations in the argument
       with an arbitrary name as key. The name is formed by concatenation of
       a prefix (such as ULS, SLS or somethink like that) and a number.

    :param loadCombinations: load combinations to be named.
    :param prefix: prefix to form the name (such as ULS, SLS or somethink like that).
    '''
    sz= len(loadCombinations) # number of combinations to name.
    szLength= int(math.log(sz,10))+1 # number of leading zeros
    retval= dict()
    for count, comb in enumerate(loadCombinations):
        key= prefix+str(count).zfill(szLength)
        retval[key]= comb
    return retval

def writeXCLoadCombinations(prefix, loadCombinations, outputFileName= None):
    ''' Write the load combinations in a XC format.

    :param loadCombinations: load combinations to be named.
    :param prefix: prefix to form the name (such as ULS, SLS or somethink like that).
    :param outputFileName: name of the output file (if None use standard output).
    '''
    if(outputFileName is None):
        f= sys.stdout
    else:
        f= open(outputFileName,'w')
    f.write("combs= loadLoader.getLoadCombinations\n")
    # Assign a name to each combination.
    namedCombinations= getNamedCombinations(loadCombinations, prefix)
    for key in namedCombinations:
        comb= namedCombinations[key]
        output= 'comb= combs.newLoadCombination('
        output+= '"'+key+'","'+comb.name+'")\n'
        f.write(output)
    if(outputFileName is None):
        f.flush()
    else:
        f.close()
