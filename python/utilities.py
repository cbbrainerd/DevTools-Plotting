# common utilities for plotting
import os
import sys
import hashlib
import glob

from DevTools.Utilities.utilities import python_mkdir, ZMASS, getCMSSWVersion

CMSSW_BASE = os.environ['CMSSW_BASE']

def hashFile(*filenames,**kwargs):
    BUFFSIZE = kwargs.pop('BUFFSIZE',65536)
    hasher = hashlib.md5()
    for filename in filenames:
        with open(filename,'rb') as f:
            buff = f.read(BUFFSIZE)
            while len(buff)>0:
                hasher.update(buff)
                buff = f.read(BUFFSIZE)
    return hasher.hexdigest()

def hashString(*strings):
    hasher = hashlib.md5()
    for string in strings:
        hasher.update(string)
    return hasher.hexdigest()



def isData(sample):
    '''Test if sample is data'''
    dataSamples = ['DoubleMuon','DoubleEG','MuonEG','SingleMuon','SingleElectron','Tau']
    return sample in dataSamples

runMap = {
    'Run2016B': 5788.,
    'Run2016C': 2573.,
    'Run2016D': 4248.,
    'Run2016E': 4009.,
    'Run2016F': 3102.,
    'Run2016G': 7540.,
    'Run2016H': 8606.,
}

runRange = {
    'Run2016B': [272760,275344],
    'Run2016C': [275656,276283],
    'Run2016D': [276315,276811],
    'Run2016E': [276831,277420],
    'Run2016F': [277932,278808],
    'Run2016G': [278820,280385],
    'Run2016H': [281613,284044],
}

def getLumi(version=getCMSSWVersion(),run=''):
    '''Get the integrated luminosity to scale monte carlo'''
    if run in runMap:
        return runMap[run]
    if version=='76X':
        #return 2263 # december jamboree golden json
        return 2318 # moriond golden json
    else:
        #return 4336.100 # previous "frozen"
        #return 12892.762 # ichep dataset golden json
        return 35867.060 # full 2016 for moriond

def getRunRange(version=getCMSSWVersion(),run=''):
    if run in runRange:
        return runRange[run]
    return [0,999999]

latestNtuples = {}
latestNtuples['76X'] = {
    'Charge'         : '2016-04-23_ChargeAnalysis_v1-merge',
    'DY'             : '2016-05-02_DYAnalysis_v1-merge',
    'DijetFakeRate'  : '',
    'Electron'       : '2016-04-14_ElectronAnalysis_v1-merge',
    'Hpp3l'          : '2016-10-16_Hpp3lAnalysis_76X_v1-merge',
    'Hpp4l'          : '2016-10-16_Hpp4lAnalysis_76X_v1-merge',
    'Muon'           : '2016-04-14_MuonAnalysis_v1-merge',
    'SingleElectron' : '',
    'SingleMuon'     : '',
    'Tau'            : '2016-05-11_TauAnalysis_v1-merge',
    'TauCharge'      : '',
    'WTauFakeRate'   : '',
    'WFakeRate'      : '',
    'WZ'             : '2016-04-29_WZAnalysis_v1-merge',
}
latestNtuples['80X'] = {
# ICHEP 2016
#    'Charge'         : '2016-11-28_ChargeAnalysis_80X_v1-merge',
#    'DY'             : '2016-09-27_DYAnalysis_80X_v1-merge',
#    'DijetFakeRate'  : '2016-11-03_DijetFakeRateAnalysis_80X_v4-merge', # hpp ids
#    'Hpp3l'          : '2016-12-19_Hpp3lAnalysis_80X_v1-merge',
#    'Hpp4l'          : '2016-12-19_Hpp4lAnalysis_80X_v1-merge',
#    'Electron'       : '2016-06-25_ElectronAnalysis_80X_v1-merge',
#    'Muon'           : '2016-06-25_MuonAnalysis_80X_v1-merge',
#    'Tau'            : '2016-07-06_TauAnalysis_80X_v1-merge',
#    'TauCharge'      : '2016-07-24_TauChargeAnalysis_80X_v1-merge',
#    'WTauFakeRate'   : '2016-07-24_WTauFakeRateAnalysis_80X_v1-merge',
#    'WFakeRate'      : '2016-07-24_WFakeRateAnalysis_80X_v1-merge',
#    'ZFakeRate'      : '2016-07-24_ZFakeRateAnalysis_80X_v1-merge',
#    'WZ'             : '2016-11-27_WZAnalysis_80X_v1-merge',
#    'ZZ'             : '2016-08-08_ZZAnalysis_80X_v1-merge',
#    'ThreeLepton'    : '2017-01-05_ThreeLeptonAnalysis_80X_v1-merge',
# Moriond 2017
    'Tau'            : '2017-03-30_TauAnalysis_80X_Moriond_v1-merge',
    'Charge'         : '2017-04-06_ChargeAnalysis_80X_Moriond_v1-merge',
    'DY'             : '2017-03-01_DYAnalysis_80X_Moriond_v2-merge',
    #'DijetFakeRate'  : '2017-04-19_DijetFakeRateAnalysis_80X_Moriond_v1-merge',
    'DijetFakeRate'  : '2017-04-20_DijetFakeRateAnalysis_80X_Moriond_v1-merge', # with tight muon
    'ZFakeRate'      : '2017-03-21_ZFakeRateAnalysis_80X_Moriond_v1-merge',
    'WFakeRate'      : '2017-03-24_WFakeRateAnalysis_80X_Moriond_v1-merge',
    'WTauFakeRate'   : '2017-03-31_WTauFakeRateAnalysis_80X_Moriond_v1-merge', # loose -0.2
    'WZ'             : '2017-04-19_WZAnalysis_80X_Moriond_v1-merge',
    'Hpp3l'          : '2017-04-26_Hpp3lAnalysis_80X_Moriond_v1-merge',
    'Hpp4l'          : '2017-04-26_Hpp4lAnalysis_80X_Moriond_v1-merge',
# Photon
    'ThreePhoton'    : '2017-06-07_ThreePhotonAnalysis_80X_Photon_v1-merge',
}

latestShifts = {}
latestShifts['80X'] = {}
latestShifts['80X']['Hpp3l'] = {
# ICHEP 2016
#    'ElectronEnUp'     : '2016-12-19_Hpp3lAnalysis_ElectronEnUp_80X_v1-merge',
#    'ElectronEnDown'   : '2016-12-19_Hpp3lAnalysis_ElectronEnDown_80X_v1-merge',
#    'MuonEnUp'         : '2016-12-19_Hpp3lAnalysis_MuonEnUp_80X_v1-merge',
#    'MuonEnDown'       : '2016-12-19_Hpp3lAnalysis_MuonEnDown_80X_v1-merge',
#    'TauEnUp'          : '2016-12-19_Hpp3lAnalysis_TauEnUp_80X_v1-merge',
#    'TauEnDown'        : '2016-12-19_Hpp3lAnalysis_TauEnDown_80X_v1-merge',
#    'JetEnUp'          : '2016-12-19_Hpp3lAnalysis_JetEnUp_80X_v1-merge',
#    'JetEnDown'        : '2016-12-19_Hpp3lAnalysis_JetEnDown_80X_v1-merge',
#    'JetResUp'         : '2016-12-19_Hpp3lAnalysis_JetResUp_80X_v1-merge',
#    'JetResDown'       : '2016-12-19_Hpp3lAnalysis_JetResDown_80X_v1-merge',
#    'UnclusteredEnUp'  : '2016-12-19_Hpp3lAnalysis_UnclusteredEnUp_80X_v1-merge',
#    'UnclusteredEnDown': '2016-12-19_Hpp3lAnalysis_UnclusteredEnDown_80X_v1-merge',
# Moriond 2017
    'ElectronEnUp'     : '2017-04-26_Hpp3lAnalysis_ElectronEnUp_80X_Moriond_v1-merge',
    'ElectronEnDown'   : '2017-04-26_Hpp3lAnalysis_ElectronEnDown_80X_Moriond_v1-merge',
    'MuonEnUp'         : '2017-04-26_Hpp3lAnalysis_MuonEnUp_80X_Moriond_v1-merge',
    'MuonEnDown'       : '2017-04-26_Hpp3lAnalysis_MuonEnDown_80X_Moriond_v1-merge',
    'TauEnUp'          : '2017-04-26_Hpp3lAnalysis_TauEnUp_80X_Moriond_v1-merge',
    'TauEnDown'        : '2017-04-26_Hpp3lAnalysis_TauEnDown_80X_Moriond_v1-merge',
}
latestShifts['80X']['Hpp4l'] = {
# ICHEP 2016
#    'ElectronEnUp'     : '2016-12-19_Hpp4lAnalysis_ElectronEnUp_80X_v1-merge',
#    'ElectronEnDown'   : '2016-12-19_Hpp4lAnalysis_ElectronEnDown_80X_v1-merge',
#    'MuonEnUp'         : '2016-12-19_Hpp4lAnalysis_MuonEnUp_80X_v1-merge',
#    'MuonEnDown'       : '2016-12-19_Hpp4lAnalysis_MuonEnDown_80X_v1-merge',
#    'TauEnUp'          : '2016-12-19_Hpp4lAnalysis_TauEnUp_80X_v1-merge',
#    'TauEnDown'        : '2016-12-19_Hpp4lAnalysis_TauEnDown_80X_v1-merge',
#    'JetEnUp'          : '2016-12-19_Hpp4lAnalysis_JetEnUp_80X_v1-merge',
#    'JetEnDown'        : '2016-12-19_Hpp4lAnalysis_JetEnDown_80X_v1-merge',
#    'JetResUp'         : '2016-12-19_Hpp4lAnalysis_JetResUp_80X_v1-merge',
#    'JetResDown'       : '2016-12-19_Hpp4lAnalysis_JetResDown_80X_v1-merge',
#    'UnclusteredEnUp'  : '2016-12-19_Hpp4lAnalysis_UnclusteredEnUp_80X_v1-merge',
#    'UnclusteredEnDown': '2016-12-19_Hpp4lAnalysis_UnclusteredEnDown_80X_v1-merge',
# Moriond 2017
    'ElectronEnUp'     : '2017-04-26_Hpp4lAnalysis_ElectronEnUp_80X_Moriond_v1-merge',
    'ElectronEnDown'   : '2017-04-26_Hpp4lAnalysis_ElectronEnDown_80X_Moriond_v1-merge',
    'MuonEnUp'         : '2017-04-26_Hpp4lAnalysis_MuonEnUp_80X_Moriond_v1-merge',
    'MuonEnDown'       : '2017-04-26_Hpp4lAnalysis_MuonEnDown_80X_Moriond_v1-merge',
    'TauEnUp'          : '2017-04-26_Hpp4lAnalysis_TauEnUp_80X_Moriond_v1-merge',
    'TauEnDown'        : '2017-04-26_Hpp4lAnalysis_TauEnDown_80X_Moriond_v1-merge',
}

def getNtupleDirectory(analysis,local=False,version=getCMSSWVersion(),shift=''):
    # first grab the local one
    if local:
        #ntupleDir = '{0}/src/ntuples/{0}'.format(CMSSW_BASE,analysis)
        ntupleDir = 'ntuples/{0}'.format(analysis)
        if os.path.exists(ntupleDir):
            return ntupleDir
    # if not read from hdfs
    baseDir = '/hdfs/store/user/dntaylor'
    if shift and analysis in latestShifts[version] and shift in latestShifts[version][analysis]:
        return os.path.join(baseDir,latestShifts[version][analysis][shift])
    if analysis in latestNtuples[version] and latestNtuples[version][analysis]:
        return os.path.join(baseDir,latestNtuples[version][analysis])

latestHistograms = {}

def getNewFlatHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    flat = 'newflat/{0}/{1}.root'.format(analysis,sample)
    return flat

def getNewProjectionHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    flat = 'newflat/{0}/{1}.root'.format(analysis,sample)
    return flat
        
def getFlatHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    flat = 'flat/{0}/{1}.root'.format(analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        flatpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(flatpath)):
            if 'projection' not in fname: flat = fname
    return flat
        
def getProjectionHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    proj = 'projections/{0}/{1}.root'.format(analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        projpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(projpath)):
            if 'projection' in fname: proj = fname
    return proj
        
latestSkims = {}
latestSkims['80X'] = {}
latestSkims['80X']['Hpp3l'] = {
# ICHEP 2016
#    #''                 : '2016-12-21_Hpp3lSkims_80X_v1',
#    'ElectronEnUp'     : '2016-12-21_Hpp3lSkims_ElectronEnUp_80X_v1',
#    'ElectronEnDown'   : '2016-12-21_Hpp3lSkims_ElectronEnDown_80X_v1',
#    'MuonEnUp'         : '2016-12-21_Hpp3lSkims_MuonEnUp_80X_v1',
#    'MuonEnDown'       : '2016-12-21_Hpp3lSkims_MuonEnDown_80X_v1',
#    'TauEnUp'          : '2016-12-21_Hpp3lSkims_TauEnUp_80X_v1',
#    'TauEnDown'        : '2016-12-21_Hpp3lSkims_TauEnDown_80X_v1',
#    'JetEnUp'          : '2016-12-21_Hpp3lSkims_JetEnUp_80X_v1',
#    'JetEnDown'        : '2016-12-21_Hpp3lSkims_JetEnDown_80X_v1',
#    'JetResUp'         : '2016-12-21_Hpp3lSkims_JetResUp_80X_v1',
#    'JetResDown'       : '2016-12-21_Hpp3lSkims_JetResDown_80X_v1',
#    'UnclusteredEnUp'  : '2016-12-21_Hpp3lSkims_UnclusteredEnUp_80X_v1',
#    'UnclusteredEnDown': '2016-12-21_Hpp3lSkims_UnclusteredEnDown_80X_v1',
#    'lepUp'            : '2016-12-21_Hpp3lSkims_lepUp_80X_v1',
#    'lepDown'          : '2016-12-21_Hpp3lSkims_lepDown_80X_v1',
#    'trigUp'           : '2016-12-21_Hpp3lSkims_trigUp_80X_v1',
#    'trigDown'         : '2016-12-21_Hpp3lSkims_trigDown_80X_v1',
#    'puUp'             : '2016-12-21_Hpp3lSkims_puUp_80X_v1',
#    'puDown'           : '2016-12-21_Hpp3lSkims_puDown_80X_v1',
#    'fakeUp'           : '2016-12-21_Hpp3lSkims_fakeUp_80X_v1',
#    'fakeDown'         : '2016-12-21_Hpp3lSkims_fakeDown_80X_v1',
# Moriond 2017
    #''                 : '2017-05-01_Hpp3lSkims_80X_v1',
    'ElectronEnUp'     : '2017-05-01_Hpp3lSkims_ElectronEnUp_80X_Moriond_v1',
    'ElectronEnDown'   : '2017-05-01_Hpp3lSkims_ElectronEnDown_80X_Moriond_v1',
    'MuonEnUp'         : '2017-05-01_Hpp3lSkims_MuonEnUp_80X_Moriond_v1',
    'MuonEnDown'       : '2017-05-01_Hpp3lSkims_MuonEnDown_80X_Moriond_v1',
    'TauEnUp'          : '2017-05-01_Hpp3lSkims_TauEnUp_80X_Moriond_v1',
    'TauEnDown'        : '2017-05-01_Hpp3lSkims_TauEnDown_80X_Moriond_v1',
    'lepUp'            : '2017-05-01_Hpp3lSkims_lepUp_80X_Moriond_v1',
    'lepDown'          : '2017-05-01_Hpp3lSkims_lepDown_80X_Moriond_v1',
    'trigUp'           : '2017-05-01_Hpp3lSkims_trigUp_80X_Moriond_v1',
    'trigDown'         : '2017-05-01_Hpp3lSkims_trigDown_80X_Moriond_v1',
    'puUp'             : '2017-05-01_Hpp3lSkims_puUp_80X_Moriond_v1',
    'puDown'           : '2017-05-01_Hpp3lSkims_puDown_80X_Moriond_v1',
    'fakeUp'           : '2017-05-01_Hpp3lSkims_fakeUp_80X_Moriond_v1',
    'fakeDown'         : '2017-05-01_Hpp3lSkims_fakeDown_80X_Moriond_v1',
}
latestSkims['80X']['Hpp4l'] = {
# ICHEP 2016
#    #''                 : '2016-12-21_Hpp4lSkims_80X_v1',
#    'ElectronEnUp'     : '2016-12-21_Hpp4lSkims_ElectronEnUp_80X_v1',
#    'ElectronEnDown'   : '2016-12-21_Hpp4lSkims_ElectronEnDown_80X_v1',
#    'MuonEnUp'         : '2016-12-21_Hpp4lSkims_MuonEnUp_80X_v1',
#    'MuonEnDown'       : '2016-12-21_Hpp4lSkims_MuonEnDown_80X_v1',
#    'TauEnUp'          : '2016-12-21_Hpp4lSkims_TauEnUp_80X_v1',
#    'TauEnDown'        : '2016-12-21_Hpp4lSkims_TauEnDown_80X_v1',
#    'JetEnUp'          : '2016-12-21_Hpp4lSkims_JetEnUp_80X_v1',
#    'JetEnDown'        : '2016-12-21_Hpp4lSkims_JetEnDown_80X_v1',
#    'JetResUp'         : '2016-12-21_Hpp4lSkims_JetResUp_80X_v1',
#    'JetResDown'       : '2016-12-21_Hpp4lSkims_JetResDown_80X_v1',
#    'UnclusteredEnUp'  : '2016-12-21_Hpp4lSkims_UnclusteredEnUp_80X_v1',
#    'UnclusteredEnDown': '2016-12-21_Hpp4lSkims_UnclusteredEnDown_80X_v1',
#    'lepUp'            : '2016-12-21_Hpp4lSkims_lepUp_80X_v1',
#    'lepDown'          : '2016-12-21_Hpp4lSkims_lepDown_80X_v1',
#    'trigUp'           : '2016-12-21_Hpp4lSkims_trigUp_80X_v1',
#    'trigDown'         : '2016-12-21_Hpp4lSkims_trigDown_80X_v1',
#    'puUp'             : '2016-12-21_Hpp4lSkims_puUp_80X_v1',
#    'puDown'           : '2016-12-21_Hpp4lSkims_puDown_80X_v1',
#    'fakeUp'           : '2016-12-21_Hpp4lSkims_fakeUp_80X_v1',
#    'fakeDown'         : '2016-12-21_Hpp4lSkims_fakeDown_80X_v1',
# Moriond 2017
    #''                 : '2017-05-01_Hpp4lSkims_80X_v2',
    'ElectronEnUp'     : '2017-05-01_Hpp4lSkims_ElectronEnUp_80X_Moriond_v2',
    'ElectronEnDown'   : '2017-05-01_Hpp4lSkims_ElectronEnDown_80X_Moriond_v2',
    'MuonEnUp'         : '2017-05-01_Hpp4lSkims_MuonEnUp_80X_Moriond_v2',
    'MuonEnDown'       : '2017-05-01_Hpp4lSkims_MuonEnDown_80X_Moriond_v2',
    'TauEnUp'          : '2017-05-01_Hpp4lSkims_TauEnUp_80X_Moriond_v2',
    'TauEnDown'        : '2017-05-01_Hpp4lSkims_TauEnDown_80X_Moriond_v2',
    'lepUp'            : '2017-05-01_Hpp4lSkims_lepUp_80X_Moriond_v2',
    'lepDown'          : '2017-05-01_Hpp4lSkims_lepDown_80X_Moriond_v2',
    'trigUp'           : '2017-05-01_Hpp4lSkims_trigUp_80X_Moriond_v2',
    'trigDown'         : '2017-05-01_Hpp4lSkims_trigDown_80X_Moriond_v2',
    'puUp'             : '2017-05-01_Hpp4lSkims_puUp_80X_Moriond_v2',
    'puDown'           : '2017-05-01_Hpp4lSkims_puDown_80X_Moriond_v2',
    'fakeUp'           : '2017-05-01_Hpp4lSkims_fakeUp_80X_Moriond_v2',
    'fakeDown'         : '2017-05-01_Hpp4lSkims_fakeDown_80X_Moriond_v2',
}

def getSkimJson(analysis,sample,version=getCMSSWVersion(),shift=''):
    jfile = 'jsons/{0}/skims/{1}.json'.format(analysis,sample)
    if shift and shift in latestSkims.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        jpath = os.path.join(baseDir,latestSkims[version][analysis][shift],sample)
        fnames = glob.glob('{0}/*.root'.format(jpath))
        if len(fnames)==0:
            raise Exception('No such path {0}'.format(jpath))
        for fname in fnames:
            if 'json' in fname: jfile = fname
    #else:
    #    raise Exception('Unrecognized {0}'.format(':'.join([analysis,sample,version,shift])))
    return jfile

def getSkimPickle(analysis,sample,version=getCMSSWVersion(),shift=''):
    pfile = 'pickles/{0}/skims/{1}.pkl'.format(analysis,sample)
    if shift and shift in latestSkims.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        ppath = os.path.join(baseDir,latestSkims[version][analysis][shift],sample)
        fnames = glob.glob('{0}/*.root'.format(ppath))
        if len(fnames)==0:
            raise Exception('No such path {0}'.format(ppath))
        for fname in fnames:
            if 'pkl' in fname: pfile = fname
    #else:
    #    raise Exception('Unrecognized {0}'.format(':'.join([analysis,sample,version,shift])))
    return pfile

treeMap = {
    ''               : 'Tree',
    'Charge'         : 'ChargeTree',
    'DijetFakeRate'  : 'DijetFakeRateTree',
    'DY'             : 'DYTree',
    'Electron'       : 'ETree',
    'Hpp3l'          : 'Hpp3lTree',
    'Hpp4l'          : 'Hpp4lTree',
    'Muon'           : 'MTree',
    'SingleElectron' : 'ETree',
    'SingleMuon'     : 'MTree',
    'Tau'            : 'TTree',
    'TauCharge'      : 'TauChargeTree',
    'WTauFakeRate'   : 'WTauFakeRateTree',
    'WFakeRate'      : 'WFakeRateTree',
    'ZFakeRate'      : 'ZFakeRateTree',
    'WZ'             : 'WZTree',
    'ZZ'             : 'ZZTree',
    'ThreeLepton'    : 'ThreeLeptonTree',
    'ThreePhoton'    : 'ThreePhotonTree',
}

def getTreeName(analysis):
    return treeMap[analysis] if analysis in treeMap else analysis+'Tree'

def addChannels(params,var,n):
    for hist in params:
        if 'yVariable' not in params[hist]: # add chans on y axis
            params[hist]['yVariable'] = var
            params[hist]['yBinning'] = [n,0,n]
        elif 'zVariable' not in params[hist]: # add chans on z axis
            params[hist]['zVariable'] = var
            params[hist]['zBinning'] = [n,0,n]
    return params

