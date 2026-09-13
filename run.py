#!/usr/bin/env python3
import sys
import os
from ar0.config import Config
from ar0.db import Database
from ar0.orchestrator import Orchestrator

def main():
    # Allow passing project directory as argument, or default to current workspace
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "projects/number_guess"

    if not os.path.exists(project_dir):
        print(f"[ERROR] Project directory '{project_dir}' does not exist.")
        sys.exit(1)

    config = Config.from_project_dir(project_dir)
    db = Database(config)
    db.init_schema()

    orchestrator = Orchestrator(config, db)
    orchestrator.run()

if __name__ == "__main__":
    main()