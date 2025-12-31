// frontend/src/hooks/useDynamicHandles.js

import { useMemo } from 'react';

/**
 * Hook for dynamic handle generation
 * 
 * Parses text fields for variable patterns ({{variable}})
 * and generates input handles dynamically.
 * 
 * This is crucial for the Text node and any future nodes
 * that need dynamic I/O based on content.
 */
export const useDynamicHandles = (schema, nodeData) => {
  const dynamicHandles = useMemo(() => {
    const result = {
      inputs: [],
      outputs: []
    };

    // Check if this node has dynamic input configuration
    if (schema.handles?.inputs?.dynamic) {
      const config = schema.handles.inputs;
      const fieldValue = nodeData[config.parseFrom] || '';
      const pattern = config.pattern;

      // Extract variables from text
      const variables = new Set();
      let match;
      
      while ((match = pattern.exec(fieldValue)) !== null) {
        variables.add(match[1].trim());
      }

      // Create handles for each unique variable
      const varsArray = Array.from(variables);
      result.inputs = varsArray.map((varName, index) => {
        // Sanitize variable name for safe handle ID
        const safeId = varName.replace(/[^a-zA-Z0-9_]/g, "_");
        
        return {
          id: safeId,
          label: varName, // Keep original for display
          position: ((index + 1) * 100) / (varsArray.length + 1)
        };
      });
    }

    return result;
  }, [schema, nodeData]);

  return dynamicHandles;
};