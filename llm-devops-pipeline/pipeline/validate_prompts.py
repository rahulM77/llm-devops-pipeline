"""
Validates that all prompt versions in the registry have required placeholders.
Run as part of CI to catch broken prompts before deployment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.rag import PROMPT_REGISTRY

REQUIRED_PLACEHOLDERS = ["{context}", "{question}"]

def validate():
    errors = []
    for version, template in PROMPT_REGISTRY.items():
        for placeholder in REQUIRED_PLACEHOLDERS:
            if placeholder not in template:
                errors.append(f"Prompt '{version}' is missing placeholder: {placeholder}")

    if errors:
        print("PROMPT VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"All {len(PROMPT_REGISTRY)} prompt versions validated successfully.")
        for v in PROMPT_REGISTRY:
            print(f"  ✓ {v}")

if __name__ == "__main__":
    validate()
