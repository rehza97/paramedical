#!/usr/bin/env python3
import os
import sys
from alembic.config import Config
from alembic import command


def run_migration():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set up Alembic configuration
    alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))

    try:
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
