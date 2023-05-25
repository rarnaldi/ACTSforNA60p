# ACTSforNA60p
ACTS for NA60+

Files needed to run the sim/rec example full_chain_na60p.py. 


INSTALLATION
==========================================
Code was checked with ACTS downloaded and built on 22/5/23. Code was run on lxplus and it is installed via:


git clone https://github.com/acts-project/acts <source>

source <source>/CI/setup_cvmfs_lcg.sh

mkdir build

cmake -B <source>/build -S ACTSsource -DACTS_BUILD_EXAMPLES_PYTHON_BINDINGS=ON -DACTS_BUILD_FATRAS=on -DACTS_BUILD_PLUGIN_TGEO=on -DACTS_BUILD_ANALYSIS_APPS=on -DCMAKE_CXX_STANDARD=17 -DACTS_BUILD_EXAMPLES=ON -DACTS_BUILD_EXAMPLES_BINARIES=ON -DACTS_BUILD_EXAMPLES_GEANT4=ON -DACTS_BUILD_PLUGIN_JSON=on

(minimum set of options to be activated)

cmake --build <source>/build/

source <source>/build/python/setup.sh

To run the sim/rec example

python3 full_chain_na60p.py



SETUP
==========
The setup consists of 5 rectangular Si layers (1.5 x 3 cm^2) along the z axis. 
The value of the magnetic field can be set in full_chain_na60p.py

example:    field = acts.ConstantBField(acts.Vector3(0.0, 1.5  * u.T, 0.0))


GEOMETRY AND MAPPING FILES
==============================
The following files contain the geometry and the mapping:

material-map.json
tgeo-config_testbeamNovember_Zorigin0.json
testbeamNovember_Zorigin0.root


SIM and REC example
==============================
The simulation and reconstruction steps are defined in 

full_chain_na60p.py


OTHER FILES
==============================
Uncertainties on the hits created during the simulation can be defined in digismear.json

The Si layers to be used in the seeding step can be set in seed_config.json


CHANGES TO BE DONE IN ACTS 
==============================
In order to run our code, few changes have to be done by hand in ACTS:

1) In Core/include/Acts/Seeding/SeedFinderConfig.hpp we set:

  float rMinMiddle = 0.f * Acts::UnitConstants::mm;
  float rMaxMiddle = 7.f * Acts::UnitConstants::mm;

(can be further tuned)

2) In Examples/Algorithms/TrackFinding/include/ActsExamples/TrackFinding/TrackParamsEstimationAlgorithm.hpp we set

    double bFieldMin = 0. * Acts::UnitConstants::T; 

to allow tracking also for very low B (not clear if tracking performances are still acceptable)

3) In Examples/Algorithms/TrackFinding/include/ActsExamples/TrackFinding/TrackParamsEstimationAlgorithm.hpp we modify the following values, used in the evaluation of the uncertainties associated to the track parameter estimate performed at the end of the seeding step.

/// Constant term of the loc0 resolution.
	double sigmaLoc0 = 5 * Acts::UnitConstants::um;
	/// Constant term of the loc1 resolution.
	double sigmaLoc1 = 5 * Acts::UnitConstants::um;
	/// Phi angular resolution.
	double sigmaPhi = 0.02 * Acts::UnitConstants::degree;
	/// Theta angular resolution.
	double sigmaTheta = 0.02 * Acts::UnitConstants::degree;
	/// q/p resolution.
	double sigmaQOverP = 0.1 / Acts::UnitConstants::GeV;
	/// Time resolution.
	double sigmaT0 = 1400 * Acts::UnitConstants::s;
	/// Inflate tracks
	std::array<double, 6> initialVarInflation = {20., 20., 10., 10., 1., 1.};



4) In Plugins/TGeo/include/Acts/Plugins/TGeo/TGeoLayerBuilder.hpp the envelope values have to be modified to allow a rectangular shape

    // Default constructor
    LayerConfig()
        : volumeName(""),
          sensorNames({}),
          localAxes("XZY"),
          envelope(std::pair<double, double>(0. * UnitConstants::mm,
                                             0.1 * UnitConstants::mm)) {}
  };


5) In Core/src/Geometry/DiscLayer.cpp remove the lines:

    aSurfaces.push_back(
        bSurfaces.at(tubeInnerCover)->surfaceRepresentation().getSharedPtr());
    aSurfaces.push_back(
        bSurfaces.at(tubeOuterCover)->surfaceRepresentation().getSharedPtr());


6) In Core/src/Geometry/Layer.cpp add one line:

  // resize to remove all items that are past the unique range
  sIntersections.resize(std::distance(sIntersections.begin(), it));

  //added
  std::sort(sIntersections.begin(), sIntersections.end(),
        	[](const auto& a, const auto& b) { return b.object->geometryId() < a.object->geometryId(); });
  // end addition


