{ lib, python3Packages }:
let
	pythonDeps = with python3Packages; [ mutagen pyyaml ];
	libSuffix = "lib/${python3Packages.python.libPrefix}/site-packages";
	pythonpath = lib.concatStringsSep ":" (map (dep: "${dep}/${libSuffix}") pythonDeps);
in
python3Packages.buildPythonPackage {
	src = null;
	name = "irank";
	propagatedBuildInputs = pythonDeps;
	pyproject = true;
	build-system = [ python3Packages.setuptools ];
	doCheck = false;
	fixupPhase =
		''
			wrapProgram "$out/bin/irank" \
				--prefix PYTHONPATH : "$out/${libSuffix}:${pythonpath}" \
				;
		'';
}
