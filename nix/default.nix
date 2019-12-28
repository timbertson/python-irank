{ lib, python3Packages, gnome3 }:
let
	pythonDeps = with python3Packages; [ mutagen pyyaml dbus-python pygobject2 ];
	libSuffix = "lib/${python3Packages.python.libPrefix}/site-packages";
	pythonpath = lib.concatStringsSep ":" (map (dep: "${dep}/${libSuffix}") pythonDeps);
in
python3Packages.buildPythonPackage {
	src = null;
	name = "irank";
	propagatedBuildInputs = pythonDeps;
	fixupPhase =
		''
			wrapProgram "$out/bin/irank" \
				--prefix PYTHONPATH : "$out/${libSuffix}:${pythonpath}" \
				;
		'';
}
