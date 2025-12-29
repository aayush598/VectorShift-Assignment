// frontend/src/nodes/nodeFactory.js

import { BaseNode } from '../components/BaseNode';
import { getNodeSchema } from '../config/nodeSchema';

/**
 * Node Factory
 * 
 * Creates node components dynamically from schemas.
 * This eliminates the need for individual node files.
 * 
 * Usage in React Flow:
 * nodeTypes = createNodeTypes()
 */

/**
 * Create a node component for a specific type
 */
export const createNodeComponent = (nodeType) => {
  return (props) => {
    const schema = getNodeSchema(nodeType);
    
    if (!schema) {
      console.error(`Schema not found for node type: ${nodeType}`);
      return null;
    }

    return (
      <BaseNode
        {...props}
        type={nodeType}
        data={{ ...props.data, schema }}
      />
    );
  };
};

/**
 * Create all node types for React Flow
 * 
 * Returns an object mapping node types to components:
 * {
 *   input: InputComponent,
 *   output: OutputComponent,
 *   llm: LLMComponent,
 *   ...
 * }
 */
export const createNodeTypes = () => {
  const nodeTypes = {};
  
  // Import all schemas
  const { nodeSchemas } = require('../config/nodeSchema');
  
  // Create a component for each schema
  Object.keys(nodeSchemas).forEach(nodeType => {
    nodeTypes[nodeType] = createNodeComponent(nodeType);
  });
  
  return nodeTypes;
};

/**
 * Alternative: Individual exports for backward compatibility
 * These are now just thin wrappers around the factory
 */
export const InputNode = createNodeComponent('input');
export const OutputNode = createNodeComponent('output');
export const LLMNode = createNodeComponent('llm');
export const TextNode = createNodeComponent('text');
export const FilterNode = createNodeComponent('filter');
export const MergeNode = createNodeComponent('merge');
export const TransformNode = createNodeComponent('transform');
export const DelayNode = createNodeComponent('delay');
export const ConditionalNode = createNodeComponent('conditional');