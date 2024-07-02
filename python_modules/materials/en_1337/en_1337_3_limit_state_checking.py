# -*- coding: utf-8 -*-
''' Reinforced rectangular elastomeric bearing design according
    to EN 1337-3:2005. Routines to perform limit state checking.
'''

from __future__ import division
from __future__ import print_function

__author__= "Luis Claudio Pérez Tato (LCPT)"
__copyright__= "Copyright 2024, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

def compute_results_under_permanent_loads_on_bearings(modelSpace, bearingElements, permLoadCombinations):
    ''' Compute the permanent loads and displacements on the given bearings.

    :param modelSpace: object wrapper of the finite element model.
    :param bearingElements: zero length finite elements corresponding to the bearings.
    :param permLoadCombinations: load combinations considered as permanent.
    '''
    retval= dict()
    for lcName in permLoadCombinations:
        lcExpr= permLoadCombinations[lcName]
        modelSpace.removeAllLoadsAndCombinationsFromDomain()
        modelSpace.revertToStart()
        modelSpace.addNewLoadCaseToDomain(loadCaseName= lcName, loadCaseExpression= lcExpr)
        result= modelSpace.analyze(calculateNodalReactions= True)

        combResults= dict()
        # extract results.
        for element in bearingElements:
            eTag= element.tag
            bearingType= element.getProp('bearing_type')
            # Get forces and displacements
            elemMaterialX= element.getMaterials()[0]
            elemMaterialY= element.getMaterials()[1]
            elemMaterialZ= element.getMaterials()[2]
            Fzd= -elemMaterialZ.getStress()
            Fxd= elemMaterialX.getStress()
            Fyd= elemMaterialY.getStress()
            vxd= abs(elemMaterialX.getStrain())
            vyd= abs(elemMaterialY.getStrain())
            # Store results
            combResults[eTag]= {'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'bearing_type':bearingType}
        retval[lcName]= combResults
    return retval
        
def compute_results_under_variable_loads_on_bearings(modelSpace, bearingElements, varLoadCombinations):
    ''' Compute the loads and displacements on the given bearings.

    :param modelSpace: object wrapper of the finite element model.
    :param bearingElements: zero length finite elements corresponding to the bearings.
    :param varLoadCombinations: load combinations to consider.
    '''
    retval= dict()
    for lcName in varLoadCombinations:
        lcExpr= varLoadCombinations[lcName]
        modelSpace.removeAllLoadsAndCombinationsFromDomain()
        modelSpace.revertToStart()
        modelSpace.addNewLoadCaseToDomain(loadCaseName= lcName, loadCaseExpression= lcExpr)
        result= modelSpace.analyze(calculateNodalReactions= True)

        combResults= dict()
        # extract results.
        for element in bearingElements:
            eTag= element.tag
            bearingType= element.getProp('bearing_type')
            # Get forces and displacements
            elemMaterialX= element.getMaterials()[0]
            elemMaterialY= element.getMaterials()[1]
            elemMaterialZ= element.getMaterials()[2]
            elemMaterialRX= element.getMaterials()[3]
            elemMaterialRY= element.getMaterials()[4]
            elemMaterialRZ= element.getMaterials()[5]
            Fzd= -elemMaterialZ.getStress()
            Fxd= elemMaterialX.getStress()
            Fyd= elemMaterialY.getStress()
            vxd= abs(elemMaterialX.getStrain())
            vyd= abs(elemMaterialY.getStrain())
            alpha_ad= abs(elemMaterialRY.getStrain())
            alpha_bd= abs(elemMaterialRX.getStrain())
            # Store results
            combResults[eTag]= {'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'alpha_ad':alpha_ad, 'alpha_bd':alpha_bd, 'comb':lcName, 'bearing_type':bearingType}
        retval[lcName]= combResults
    return retval

def compute_results_on_bearings(modelSpace, bearingElements, permLoadCombinations, varLoadCombinations):
    ''' Compute the loads and displacements on the given bearings.

    :param modelSpace: object wrapper of the finite element model.
    :param bearingElements: zero length finite elements corresponding to the bearings.
    :param varLoadCombinations: load combinations to consider.
    '''
    perm_results= compute_results_under_permanent_loads_on_bearings(modelSpace= modelSpace, bearingElements= bearingElements, permLoadCombinations= permLoadCombinations)
    var_results= compute_results_under_variable_loads_on_bearings(modelSpace= modelSpace, bearingElements= bearingElements, varLoadCombinations= varLoadCombinations)
    retval= {'perm_results':perm_results, 'var_results':var_results}
    return retval

def check_results_en_1337_3(analysisResults, bearingElements, bearingMatDict):
    ''' Perform the EN 1337-3 checkings. 

    :param loadResults: results of the analysis for the bearing elements.
    :param bearingElements: zero length finite elements corresponding to the bearings.
    :param bearingMaterials: dictionary containing the bearing materials with the bearing type as key.
    '''
    sigma_perm_results= dict()
    sliding_perm_results= dict()
    # Check beam bearings under permanent loads:
    perm_results= analysisResults['perm_results']
    bearingPermCombinations= list(perm_results.keys())
    for lcName in bearingPermCombinations:
        comb_results= perm_results[lcName]
        elemKeyType= type(list(comb_results.keys())[0]) # string if loaded from JSON
                                              # integer otherwise.
        # extract results.
        for element in bearingElements:
            eTag= element.tag
            # Get element position
            centroid= element.getPosCentroid(True)
            elem_results= comb_results[elemKeyType(eTag)]
            bearingType= elem_results['bearing_type']
            # bearingType= element.getProp('bearing_type')
            bearingMat= bearingMatDict[bearingType]
            # Get forces and displacements
            Fzd= elem_results['Fzd']
            vxd= elem_results['vxd']
            vyd= elem_results['vyd']
            # Check minimum stress
            sigma_perm_cf= bearingMat.getPermCompressiveStressEfficiency(vxd= vxd, vyd= vyd, Fzd_min_perm= Fzd)
            if(eTag in sigma_perm_results):
                results= sigma_perm_results[eTag]
                cf= results['sigma_perm_cf']
                if(sigma_perm_cf>cf): # Update worst-case for the element.
                    sigma_perm= bearingMat.getCompressiveStress(vxd= vxd, vyd= vyd, Fzd= Fzd)
                    sigma_perm_results[eTag]= {'sigma_perm_cf':sigma_perm_cf, 'sigma_perm':sigma_perm, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                sigma_perm= bearingMat.getCompressiveStress(vxd= vxd, vyd= vyd, Fzd= Fzd)
                sigma_perm_results[eTag]= {'sigma_perm_cf':sigma_perm_cf, 'sigma_perm':sigma_perm, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            # Check friction
            Fxd= elem_results['Fxd']
            Fyd= elem_results['Fyd']
            sliding_perm_cf= bearingMat.getSlidingConditionEfficiency(vxd= vxd, vyd= vyd, Fxd= Fxd, Fyd= Fyd, Fzd_min= Fzd, concreteBedding= True)
            if(eTag in sliding_perm_results):
                results= sliding_perm_results[eTag]
                cf= results['sliding_perm_cf']
                if(sliding_perm_cf>cf):
                    friction_coef= bearingMat.getFrictionCoefficient(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                    friction_force= bearingMat.getFrictionForce(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                    sliding_perm_results[eTag]= {'sliding_perm_cf':sliding_perm_cf, 'friction_coef':friction_coef, 'friction_force':friction_force, 'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                friction_coef= bearingMat.getFrictionCoefficient(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                friction_force= bearingMat.getFrictionForce(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                sliding_perm_results[eTag]= {'sliding_perm_cf':sliding_perm_cf, 'friction_coef':friction_coef, 'friction_force':friction_force, 'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
    # Store results in retval variable.
    perm_check_results= {'sigma_perm_results':sigma_perm_results, 'sliding_perm_results':sliding_perm_results}
    retval= {'perm_check_results':perm_check_results}

    # Check beam bearings under SLS loads:
    var_results= analysisResults['var_results']
    bearingCombinations= list(var_results.keys())
    total_strain_results= dict()
    laminate_thickness_results= dict()
    buckling_stability_results= dict()
    rotational_deflection_results= dict()
    sliding_var_results= dict()
    for lcName in bearingCombinations:
        comb_results= var_results[lcName]
        elemKeyType= type(list(comb_results.keys())[0]) # string if loaded from JSON
                                              # integer otherwise.
        # extract results.
        for element in bearingElements:
            eTag= element.tag
            # Get element position.
            centroid= element.getPosCentroid(True)
            elem_results= comb_results[elemKeyType(eTag)]
            bearingType= elem_results['bearing_type']
            # Get bearing material.
            #bearingType= element.getProp('bearing_type')
            bearingMat= bearingMatDict[bearingType]
            # Get forces and displacements
            Fxd= elem_results['Fxd']
            Fyd= elem_results['Fyd']
            Fzd= elem_results['Fzd']
            vxd= elem_results['vxd']
            vyd= elem_results['vyd']
            alpha_ad= elem_results['alpha_ad']
            alpha_bd= elem_results['alpha_bd']
            # Check total strain
            total_strain_cf= bearingMat.getTotalStrainEfficiency(vxd= vxd, vyd= vyd, Fzd= Fzd, alpha_ad= alpha_ad, alpha_bd= alpha_bd)
            if(eTag in total_strain_results):
                results= total_strain_results[eTag]
                cf= results['total_strain_cf']
                if(total_strain_cf>cf): # Update worst-case for the element.
                    total_strain= bearingMat.getTotalStrain(vxd= vxd, vyd= vyd, Fzd= Fzd, alpha_ad= alpha_ad, alpha_bd= alpha_bd)
                    compressive_strain_inner= bearingMat.getCompressiveStrain(vxd= vxd, vyd= vyd, Fzd= Fzd, innerLayer= True)
                    compressive_strain_outer= bearingMat.getCompressiveStrain(vxd= vxd, vyd= vyd, Fzd= Fzd, innerLayer= False)
                    shear_strain= bearingMat.getShearStrain(vxd= vxd, vyd= vyd)
                    rotation_strain= bearingMat.getAngularRotationStrain(alpha_ad= alpha_ad, alpha_bd= alpha_bd)
                    total_strain_results[eTag]= {'total_strain_cf':total_strain_cf, 'total_strain':total_strain, 'compressive_strain_inner':compressive_strain_inner, 'compressive_strain_outer':compressive_strain_outer, 'shear_strain':shear_strain, 'rotation_strain':rotation_strain, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'alpha_ad':alpha_ad, 'alpha_bd':alpha_bd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                total_strain= bearingMat.getCompressiveStress(vxd= vxd, vyd= vyd, Fzd= Fzd)
                compressive_strain_inner= bearingMat.getCompressiveStrain(vxd= vxd, vyd= vyd, Fzd= Fzd, innerLayer= True)
                compressive_strain_outer= bearingMat.getCompressiveStrain(vxd= vxd, vyd= vyd, Fzd= Fzd, innerLayer= False)
                shear_strain= bearingMat.getShearStrain(vxd= vxd, vyd= vyd)
                rotation_strain= bearingMat.getAngularRotationStrain(alpha_ad= alpha_ad, alpha_bd= alpha_bd)
                total_strain_results[eTag]= {'total_strain_cf':total_strain_cf, 'total_strain':total_strain, 'compressive_strain_inner':compressive_strain_inner, 'compressive_strain_outer':compressive_strain_outer, 'shear_strain':shear_strain, 'rotation_strain':rotation_strain, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'alpha_ad':alpha_ad, 'alpha_bd':alpha_bd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            # Check minimum thickness of steel laminate.
            laminate_thickness_cf= bearingMat.getPlateThicknessEfficiency(vxd= vxd, vyd= vyd, Fzd= Fzd, withHoles= False)
            if(eTag in laminate_thickness_results):
                results= laminate_thickness_results[eTag]
                cf= results['laminate_thickness_cf']
                if(laminate_thickness_cf>cf): # Update worst-case for the element.
                    req_laminate_thickness= bearingMat.getRequiredReinforcedPlateThickness(vxd= vxd, vyd= vyd, Fzd= Fzd, withHoles= False)
                    laminate_thickness_results[eTag]= {'laminate_thickness_cf':laminate_thickness_cf, 'req_laminate_thickness':req_laminate_thickness, 'laminate_thickness':bearingMat.ts, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'with_holes':False, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                req_laminate_thickness= bearingMat.getRequiredReinforcedPlateThickness(vxd= vxd, vyd= vyd, Fzd= Fzd, withHoles= False)
                laminate_thickness_results[eTag]= {'laminate_thickness_cf':laminate_thickness_cf, 'req_laminate_thickness':req_laminate_thickness, 'laminate_thickness':bearingMat.ts, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'with_holes':False, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            # Check buckling stability of steel laminate.
            buckling_stability_cf= bearingMat.getBucklingEfficiency(vxd= vxd, vyd= vyd, Fzd= Fzd)
            if(eTag in buckling_stability_results):
                results= buckling_stability_results[eTag]
                cf= results['buckling_stability_cf']
                if(buckling_stability_cf>cf): # Update worst-case for the element.
                    buckling_stability_results[eTag]= {'buckling_stability_cf':buckling_stability_cf, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                buckling_stability_results[eTag]= {'buckling_stability_cf':buckling_stability_cf, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            # Check rotational deflection.
            rotational_deflection_cf= bearingMat.getRotationalLimitEfficiency(vxd= vxd, vyd= vyd, Fzd= Fzd, alpha_ad= alpha_ad, alpha_bd= alpha_bd)
            if(eTag in rotational_deflection_results):
                results= rotational_deflection_results[eTag]
                cf= results['rotational_deflection_cf']
                if(rotational_deflection_cf>cf): # Update worst-case for the element.
                    vertical_deflection= bearingMat.getTotalVerticalDeflection(vxd= vxd, vyd= vyd, Fzd= Fzd)
                    rotational_deflection= bearingMat.getRotationalDeflection(alpha_ad= alpha_ad, alpha_bd= alpha_bd)
                    rotational_deflection_results[eTag]= {'rotational_deflection_cf':rotational_deflection_cf, 'rotational_deflection':rotational_deflection, 'vertical_deflection':vertical_deflection, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'alpha_ad':alpha_ad, 'alpha_bd':alpha_bd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                vertical_deflection= bearingMat.getTotalVerticalDeflection(vxd= vxd, vyd= vyd, Fzd= Fzd)
                rotational_deflection= bearingMat.getRotationalDeflection(alpha_ad= alpha_ad, alpha_bd= alpha_bd)
                rotational_deflection_results[eTag]= {'rotational_deflection_cf':rotational_deflection_cf, 'rotational_deflection':rotational_deflection, 'vertical_deflection':vertical_deflection, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'alpha_ad':alpha_ad, 'alpha_bd':alpha_bd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            # Check friction.
            sliding_cf= bearingMat.getSlidingConditionEfficiency(vxd= vxd, vyd= vyd, Fxd= Fxd, Fyd= Fyd, Fzd_min= Fzd, concreteBedding= True)
            if(eTag in sliding_var_results):
                results= sliding_var_results[eTag]
                cf= results['sliding_cf']
                if(sliding_cf>cf): # Update worst-case for the element.
                    friction_coef= bearingMat.getFrictionCoefficient(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                    friction_force= bearingMat.getFrictionForce(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                    sliding_var_results[eTag]= {'sliding_cf':sliding_cf, 'friction_coef':friction_coef, 'friction_force':friction_force, 'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
            else: # no data for this element yet.
                friction_coef= bearingMat.getFrictionCoefficient(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                friction_force= bearingMat.getFrictionForce(vxd= vxd, vyd= vyd, Fzd_min= Fzd, concreteBedding= True)
                sliding_var_results[eTag]= {'sliding_cf':sliding_cf, 'friction_coef':friction_coef, 'friction_force':friction_force, 'Fxd':Fxd, 'Fyd':Fyd, 'Fzd':Fzd, 'vxd':vxd, 'vyd':vyd, 'comb':lcName, 'bearing_type':bearingType, 'x': centroid.x, 'y':centroid.y, 'z':centroid.z}
    # Store results in retval variable.
    var_check_results= {'total_strain_results': total_strain_results, 'laminate_thickness_results': laminate_thickness_results, 'buckling_stability_results': buckling_stability_results, 'rotational_deflection_results': rotational_deflection_results, 'sliding_var_results': sliding_var_results} 
    retval.update({'var_check_results':var_check_results})
    return retval

