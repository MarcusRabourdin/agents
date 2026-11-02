{
  description = "Online chess platform - FastAPI server and React frontend";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      forAllSystems = f:
        nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      # Mirrors backend/requirements.txt. Keep the two in step: requirements.txt
      # is what a plain pip/venv setup uses, this is what Nix provides.
      pythonPackages = ps: with ps; [
        fastapi
        pydantic
        chess # python-chess, the rules engine
        pyyaml # used by scripts/export_swagger.py

        # uvicorn[standard]
        uvicorn
        uvloop
        httptools
        websockets
        watchfiles
        python-dotenv

        # Tests
        pytest
        httpx2 # what starlette's TestClient wants
      ];

      pythonEnv = pkgs: pkgs.python313.withPackages pythonPackages;
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          name = "chess-platform";

          packages = [
            (pythonEnv pkgs)
            pkgs.nodejs_22
            pkgs.ruff # python linter / formatter
          ];

          shellHook = ''
            echo "chess-platform dev shell"
            echo "  uvicorn app.main:app --reload --app-dir backend   # serve"
            echo "  pytest backend/tests                              # tests"
            echo "  python backend/scripts/export_swagger.py          # spec"
            echo "  npm --prefix frontend install && npm --prefix frontend run dev"
          '';
        };
      });

      # nix flake check runs the backend test suite.
      checks = forAllSystems (pkgs: {
        backend = pkgs.runCommand "backend-tests"
          {
            nativeBuildInputs = [ (pythonEnv pkgs) ];
          } ''
          cp -r ${./backend} backend
          chmod -R u+w backend
          cd backend
          export HOME="$TMPDIR"
          pytest
          touch "$out"
        '';
      });

      # nix run - serves the backend from the current checkout, so --reload
      # picks up edits. Run it from the repository root.
      apps = forAllSystems (pkgs: {
        default = {
          type = "app";
          program = pkgs.lib.getExe (pkgs.writeShellApplication {
            name = "serve-chess-api";
            runtimeInputs = [ (pythonEnv pkgs) ];
            text = ''
              if [ ! -d backend/app ]; then
                echo "run this from the repository root" >&2
                exit 1
              fi
              exec uvicorn app.main:app --reload --app-dir backend "$@"
            '';
          });
        };
      });

      packages = forAllSystems (pkgs: {
        # The exact interpreter + libraries the backend runs on.
        default = pythonEnv pkgs;
      });

      formatter = forAllSystems (pkgs: pkgs.nixpkgs-fmt);
    };
}
