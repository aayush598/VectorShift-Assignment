// frontend/src/config/nodeSchema.js

/**
 * Node Schema Registry
 * 
 * This file defines all node types as declarative schemas.
 * Adding a new node is simply adding a new entry here - no new components needed.
 */

export const NODE_CATEGORIES = {
  INPUT: 'Input',
  OUTPUT: 'Output',
  PROCESSOR: 'Processor',
  TRANSFORM: 'Transform',
  UTILITY: 'Utility'
};

export const FIELD_TYPES = {
  TEXT: 'text',
  TEXTAREA: 'textarea',
  SELECT: 'select',
  NUMBER: 'number',
  CHECKBOX: 'checkbox',
  COLOR: 'color'
};

export const nodeSchemas = {
  input: {
    type: 'input',
    label: 'Input',
    category: NODE_CATEGORIES.INPUT,
    description: 'Input data source',
    icon: 'MdInput',
    showInToolbar: true,
    toolbarOrder: 1,
    fields: [
      {
        name: 'inputName',
        label: 'Name',
        type: FIELD_TYPES.TEXT,
        default: (id) => id.replace('customInput-', 'input_'),
        required: true
      },
      {
        name: 'inputType',
        label: 'Type',
        type: FIELD_TYPES.SELECT,
        options: ['Text', 'File', 'Number', 'Boolean'],
        default: 'Text',
        required: true
      }
    ],
    handles: {
      inputs: [],
      outputs: [
        { id: 'output', label: 'Output' }
      ]
    },
    style: {
      variant: 'input',
      color: '#3b82f6'
    }
  },

  output: {
    type: 'output',
    label: 'Output',
    category: NODE_CATEGORIES.OUTPUT,
    description: 'Output destination',
    icon: 'MdOutlineOutput',
    showInToolbar: true,
    toolbarOrder: 2,
    fields: [
      {
        name: 'outputName',
        label: 'Name',
        type: FIELD_TYPES.TEXT,
        default: (id) => id.replace('customOutput-', 'output_'),
        required: true
      },
      {
        name: 'outputType',
        label: 'Type',
        type: FIELD_TYPES.SELECT,
        options: ['Text', 'File', 'Image'],
        default: 'Text',
        required: true
      }
    ],
    handles: {
      inputs: [
        { id: 'input', label: 'Input' }
      ],
      outputs: []
    },
    style: {
      variant: 'output',
      color: '#10b981'
    }
  },

  llm: {
    type: 'llm',
    label: 'LLM',
    category: NODE_CATEGORIES.PROCESSOR,
    description: 'Large Language Model processor',
    icon: 'TbBoxModel2',
    showInToolbar: true,
    toolbarOrder: 3,
    fields: [
      {
        name: 'modelName',
        label: 'Model',
        type: FIELD_TYPES.SELECT,
        options: ['GPT-4', 'GPT-3.5', 'Claude', 'Llama'],
        default: 'GPT-4'
      },
      {
        name: 'temperature',
        label: 'Temperature',
        type: FIELD_TYPES.NUMBER,
        default: 0.7,
        min: 0,
        max: 2,
        step: 0.1
      }
    ],
    handles: {
      inputs: [
        { id: 'system', label: 'System', position: 33 },
        { id: 'prompt', label: 'Prompt', position: 66 }
      ],
      outputs: [
        { id: 'response', label: 'Response' }
      ]
    },
    style: {
      variant: 'processor',
      color: '#8b5cf6'
    }
  },

  text: {
    type: 'text',
    label: 'Text',
    category: NODE_CATEGORIES.INPUT,
    description: 'Static or dynamic text with variable support',
    icon: 'CiText',
    showInToolbar: true,
    toolbarOrder: 4,
    fields: [
      {
        name: 'text',
        label: 'Text',
        type: FIELD_TYPES.TEXTAREA,
        default: '',
        placeholder: 'Enter text... Use {{variable}} for dynamic inputs',
        rows: 4
      }
    ],
    handles: {
      inputs: {
        dynamic: true,
        parseFrom: 'text',
        pattern: /\{\{([^}]+)\}\}/g
      },
      outputs: [
        { id: 'output', label: 'Output' }
      ]
    },
    style: {
      variant: 'input',
      color: '#06b6d4'
    }
  },

  // NEW NODES - Demonstrating abstraction flexibility

  filter: {
    type: 'filter',
    label: 'Filter',
    category: NODE_CATEGORIES.TRANSFORM,
    description: 'Filter data based on conditions',
    icon: 'TbFilter',
    showInToolbar: true,
    toolbarOrder: 5,
    fields: [
      {
        name: 'filterType',
        label: 'Filter Type',
        type: FIELD_TYPES.SELECT,
        options: ['Contains', 'Equals', 'Greater Than', 'Less Than', 'Regex'],
        default: 'Contains'
      },
      {
        name: 'condition',
        label: 'Condition',
        type: FIELD_TYPES.TEXT,
        default: '',
        placeholder: 'Enter filter condition'
      },
      {
        name: 'caseSensitive',
        label: 'Case Sensitive',
        type: FIELD_TYPES.CHECKBOX,
        default: false
      }
    ],
    handles: {
      inputs: [
        { id: 'input', label: 'Input' }
      ],
      outputs: [
        { id: 'match', label: 'Match', position: 33 },
        { id: 'nomatch', label: 'No Match', position: 66 }
      ]
    },
    style: {
      variant: 'transform',
      color: '#f59e0b'
    }
  },

  merge: {
    type: 'merge',
    label: 'Merge',
    category: NODE_CATEGORIES.UTILITY,
    description: 'Combine multiple inputs',
    icon: 'MdMergeType',
    showInToolbar: true,
    toolbarOrder: 6,
    fields: [
      {
        name: 'mergeStrategy',
        label: 'Strategy',
        type: FIELD_TYPES.SELECT,
        options: ['Concatenate', 'Join with Delimiter', 'Array', 'Object'],
        default: 'Concatenate'
      },
      {
        name: 'delimiter',
        label: 'Delimiter',
        type: FIELD_TYPES.TEXT,
        default: ', ',
        placeholder: 'Enter delimiter'
      }
    ],
    handles: {
      inputs: [
        { id: 'input1', label: 'Input 1', position: 25 },
        { id: 'input2', label: 'Input 2', position: 50 },
        { id: 'input3', label: 'Input 3', position: 75 }
      ],
      outputs: [
        { id: 'output', label: 'Output' }
      ]
    },
    style: {
      variant: 'utility',
      color: '#ec4899'
    }
  },

  transform: {
    type: 'transform',
    label: 'Transform',
    category: NODE_CATEGORIES.TRANSFORM,
    description: 'Transform data format or structure',
    icon: 'TbTransform',
    showInToolbar: true,
    toolbarOrder: 7,
    fields: [
      {
        name: 'transformation',
        label: 'Transformation',
        type: FIELD_TYPES.SELECT,
        options: ['Uppercase', 'Lowercase', 'Title Case', 'JSON Parse', 'JSON Stringify', 'Trim', 'Reverse'],
        default: 'Uppercase'
      },
      {
        name: 'preserveWhitespace',
        label: 'Preserve Whitespace',
        type: FIELD_TYPES.CHECKBOX,
        default: true
      }
    ],
    handles: {
      inputs: [
        { id: 'input', label: 'Input' }
      ],
      outputs: [
        { id: 'output', label: 'Output' }
      ]
    },
    style: {
      variant: 'transform',
      color: '#14b8a6'
    }
  },

  delay: {
    type: 'delay',
    label: 'Delay',
    category: NODE_CATEGORIES.UTILITY,
    description: 'Add delay to data flow',
    icon: 'MdOutlineTimer',
    showInToolbar: true,
    toolbarOrder: 8,
    fields: [
      {
        name: 'delayMs',
        label: 'Delay (ms)',
        type: FIELD_TYPES.NUMBER,
        default: 1000,
        min: 0,
        max: 10000,
        step: 100
      },
      {
        name: 'enableDelay',
        label: 'Enable Delay',
        type: FIELD_TYPES.CHECKBOX,
        default: true
      }
    ],
    handles: {
      inputs: [
        { id: 'input', label: 'Input' }
      ],
      outputs: [
        { id: 'output', label: 'Output' }
      ]
    },
    style: {
      variant: 'utility',
      color: '#64748b'
    }
  },

  conditional: {
    type: 'conditional',
    label: 'Conditional',
    category: NODE_CATEGORIES.PROCESSOR,
    description: 'Route data based on conditions',
    icon: 'MdCallSplit',
    showInToolbar: true,
    toolbarOrder: 9,
    fields: [
      {
        name: 'condition',
        label: 'Condition',
        type: FIELD_TYPES.TEXT,
        default: '',
        placeholder: 'e.g., value > 10'
      },
      {
        name: 'operator',
        label: 'Operator',
        type: FIELD_TYPES.SELECT,
        options: ['==', '!=', '>', '<', '>=', '<=', 'contains', 'startsWith', 'endsWith'],
        default: '=='
      },
      {
        name: 'compareValue',
        label: 'Compare To',
        type: FIELD_TYPES.TEXT,
        default: ''
      }
    ],
    handles: {
      inputs: [
        { id: 'input', label: 'Input' }
      ],
      outputs: [
        { id: 'true', label: 'True', position: 33 },
        { id: 'false', label: 'False', position: 66 }
      ]
    },
    style: {
      variant: 'processor',
      color: '#f97316'
    }
  }
};

/**
 * Get schema by node type
 */
export const getNodeSchema = (type) => {
  return nodeSchemas[type] || null;
};

/**
 * Get all schemas by category
 */
export const getNodesByCategory = (category) => {
  return Object.values(nodeSchemas).filter(
    schema => schema.category === category
  );
};

/**
 * Get all node types
 */
export const getAllNodeTypes = () => {
  return Object.keys(nodeSchemas);
};