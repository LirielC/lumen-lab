

import sys
from app.bootstrap.application import create_app


def main() -> int:
    
    app, container = create_app()
    if len(sys.argv) == 3 and sys.argv[1] == "--verify-release":
        from pathlib import Path
        from app.bootstrap.installation_check import run_installation_check
        return run_installation_check(app, container, Path(sys.argv[2]))
    container.main_window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
