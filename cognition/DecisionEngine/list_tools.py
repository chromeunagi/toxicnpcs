#!/usr/bin/env python
"""List all registered tools in the toolbox."""

import sys
import os

# Add parent directory to path so imports work properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cognition.DecisionEngine.toolbox import _TOOL_REGISTRY

def main():
    """Print out all registered tools."""
    print(f"Total number of tools: {len(_TOOL_REGISTRY)}")
    print("\nAvailable tools by category:")
    
    # Group tools by their module
    tools_by_module = {}
    for tool_name, tool_class in _TOOL_REGISTRY.items():
        module_name = tool_class.__module__.split('.')[-1]
        if module_name not in tools_by_module:
            tools_by_module[module_name] = []
        tools_by_module[module_name].append((tool_name, tool_class.description))
    
    # Print tools by module
    for module_name, tools in sorted(tools_by_module.items()):
        print(f"\n{module_name.replace('_tools', '').capitalize()} Tools:")
        for tool_name, description in sorted(tools):
            print(f"- {tool_name}: {description}")
    
if __name__ == "__main__":
    main() 