{ lib, pythonPackages, gnome3 }:
let
	pythonDeps = with pythonPackages; [ mutagen pyyaml dbus-python pygobject2 ];
	libSuffix = "lib/${pythonPackages.python.libPrefix}/site-packages";
	pythonpath = lib.concatStringsSep ":" (map (dep: "${dep}/${libSuffix}") pythonDeps);
in
pythonPackages.buildPythonPackage {
	src = ./local.tgz;
	name = "irank";
	propagatedBuildInputs = pythonDeps;
	fixupPhase =
		''
			wrapProgram "$out/bin/irank" \
				--prefix PYTHONPATH : "$out/${libSuffix}:${pythonpath}" \
				;
		'';
}
