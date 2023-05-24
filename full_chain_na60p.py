#!/usr/bin/env python3
import pathlib, acts, acts.examples
from acts.examples.simulation import (
    addParticleGun,
    MomentumConfig,
    EtaConfig,
    ParticleConfig,
    addPythia8,
    addFatras,
    ParticleSelectorConfig,
    addDigitization,
)
from acts.examples.reconstruction import (
    addSeeding,
    TruthSeedRanges,
    SeedFinderConfigArg,
    SeedFinderOptionsArg,
    SeedFilterConfigArg,
    SpacePointGridConfigArg,
    SeedingAlgorithmConfigArg,
    SeedingAlgorithm,
    ParticleSmearingSigmas,
    addCKFTracks,
    CKFPerformanceConfig,        
    TrackSelectorRanges,
    addAmbiguityResolution,
    AmbiguityResolutionConfig,
    addVertexFitting,
    VertexFinder,
)
from acts.examples import TGeoDetector

ttbar_pu200 = False
u = acts.UnitConstants
outputDir = pathlib.Path.cwd() / "fullchain_output"

matDeco = acts.IMaterialDecorator.fromFile("material-map.json")
jsonFile="tgeo-config_testbeamNovember_Zorigin0.json"
tgeo_fileName= "testbeamNovember_Zorigin0.root "

logLevel=acts.logging.VERBOSE
customLogLevel = acts.examples.defaultLogging(logLevel=logLevel)

detector, trackingGeometry, decorators = TGeoDetector.create(jsonFile=str(jsonFile),
      fileName=str(tgeo_fileName),
      surfaceLogLevel=customLogLevel(),
      layerLogLevel=customLogLevel(),
      volumeLogLevel=customLogLevel(),
      mdecorator=matDeco,
)

#field = acts.ConstantBField(acts.Vector3(0.5  * u.T, 0.0  * u.T, 0.0))  #~dipole field
#field = acts.ConstantBField(acts.Vector3(0.0, 0.05  * u.T, 0.0))  #~dipole field
#field = acts.ConstantBField(acts.Vector3(0.0, 0, 0.00005 * u.T))  #it seems B is needed
field = acts.ConstantBField(acts.Vector3(0.0, 0, 0.05 * u.T))  #it seems B is needed


rnd = acts.examples.RandomNumbers(seed=44)

s = acts.examples.Sequencer(events=100, numThreads=1, outputDir=str(outputDir))

if not ttbar_pu200:
    addParticleGun(
        s,
        MomentumConfig(2.0 * u.GeV, 10.0 * u.GeV, transverse=False),
        EtaConfig(3.6,5.2, uniform=True),
        ParticleConfig(1, acts.PdgParticle.eMuon, randomizeCharge=True),
	multiplicity=1,
	vtxGen=acts.examples.GaussianVertexGenerator(
        stddev=acts.Vector4(0.0 * u.mm, 0.0 * u.mm, 0.0 * u.mm, 0 * u.ns),
        mean=acts.Vector4(0, 0, 0, 0),
        ),

        rnd=rnd,
        outputDirRoot=outputDir,
    )
else:
    addPythia8(
        s,
        hardProcess=["Top:qqbar2ttbar=on"],
        npileup=200,
        vtxGen=acts.examples.GaussianVertexGenerator(
            stddev=acts.Vector4(0.0125 * u.mm, 0.0125 * u.mm, 55.5 * u.mm, 5.0 * u.ns),
            mean=acts.Vector4(0, 0, 0, 0),
        ),
        rnd=rnd,
        outputDirRoot=outputDir,
    )

addFatras(
    s,
    trackingGeometry,
    field,
    rnd,
    ParticleSelectorConfig(eta=(None, None), pt=(150 * u.MeV, None), removeNeutral=True) 
    if ttbar_pu200
    else ParticleSelectorConfig(),  #I'm not applying a selection
    outputDirRoot=outputDir,
)

addDigitization(
    s,
    trackingGeometry,
    field,
    digiConfigFile="digismear.json",
    outputDirRoot=outputDir,
    outputDirCsv="test",
    rnd=rnd,
)

addSeeding(
    s,
    trackingGeometry,
    field,
    TruthSeedRanges(eta=(None, None), nHits=(3, None)),
    SeedFinderConfigArg(
        r=(0.5 * u.mm, 7 * u.mm),  
        deltaR=(0.01 * u.mm, 2.5 * u.mm),      # check if we should keep 2.5             
        collisionRegion=(-50 * u.mm, 50 * u.mm),   
        z=(20 * u.mm, 130 * u.mm),  
        maxSeedsPerSpM=5,    
        sigmaScattering=5.,   
        radLengthPerSeed=0.05,  
        minPt=0 * u.MeV, 
        impactMax=5. * u.mm, 
        cotThetaMax= 250, 
        seedConfirmation=False, 
         forwardSeedConfirmationRange=acts.SeedConfirmationRangeConfig( #it should not be used....
            zMinSeedConf=-1220 * u.mm,
            zMaxSeedConf=1220 * u.mm,
            rMaxSeedConf=36 * u.mm,
            nTopForLargeR=1,
            nTopForSmallR=2,
        ),
        skipPreviousTopSP=False,  
        useVariableMiddleSPRange=False, #MODIFICATO 22/5/23
        # deltaRMiddleSPRange=(0 * u.mm, 7 * u.mm), #not useful if useVariableMiddleSPRange=False
        deltaRTopSP=(0.001 * u.mm, 7 * u.mm),
        deltaRBottomSP=(0.001 * u.mm, 7 * u.mm),
    ),
    SeedFinderOptionsArg(bFieldInZ=0 * u.T, beamPos=(0 * u.mm, 0 * u.mm)),  #why should I give the b field?
    SeedFilterConfigArg(    #not used, why?
        seedConfirmation=False,
        maxSeedsPerSpMConf=5,
        maxQualitySeedsPerSpMConf=5,
    ),
        SpacePointGridConfigArg(
         zBinEdges=[12.5, 37.5, 62.5, 87.5, 112.5, 137.5],
         impactMax=0.1 * u.mm,
         phiBinDeflectionCoverage=1,
    ),
        SeedingAlgorithmConfigArg(
        zBinNeighborsTop=[[0,1],[0,1],[0,1],[0,1],[0,1]],
        zBinNeighborsBottom=[[-1,0],[-1,0],[-1,0],[-1,0],[-1,0]],
        numPhiNeighbors=1,
    ),
    #    seedingAlgorithm=SeedingAlgorithm.TruthEstimated,  
#    seedingAlgorithm=SeedingAlgorithm.Orthogonal,  
    seedingAlgorithm=SeedingAlgorithm.Default,  

    geoSelectionConfigFile="seed_config.json",
    outputDirRoot=outputDir,
)

addCKFTracks(
    s,
    trackingGeometry,
    field,
    CKFPerformanceConfig(ptMin=1.0 * u.GeV if ttbar_pu200 else 0.0, nMeasurementsMin=5),
    TrackSelectorRanges(pt=(None, None), absEta=(None, None)),
#    TrackSelectorRanges(pt=(None, None), absEta=(None, None), removeNeutral=True),
    outputDirRoot=outputDir,
    logLevel=acts.logging.DEBUG,
)

#addAmbiguityResolution(
#   s,
#    AmbiguityResolutionConfig(maximumSharedHits=3),
#    CKFPerformanceConfig(ptMin=1.0 * u.GeV if ttbar_pu200 else 0.0, nMeasurementsMin=5),
#    outputDirRoot=outputDir,
#)
#
#addVertexFitting(
#    s,
#    field,
#    vertexFinder=VertexFinder.Iterative,
#    outputDirRoot=outputDir,
#)

s.run()
