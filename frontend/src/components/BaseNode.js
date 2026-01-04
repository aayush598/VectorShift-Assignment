// frontend/src/components/BaseNode.js

import { Handle, Position } from "reactflow";
import { useState, useEffect } from "react";
import FieldRenderer from "./FieldRenderer";
import { useDynamicHandles } from "../hooks/useDynamicHandles";
import { useStore } from "../store";
import { NODE_ICONS } from "../config/nodeIcons";

/**
 * BaseNode - Universal node renderer
 * 
 * This component renders ANY node type based on its schema.
 * No new components needed for new nodes.
 */
export const BaseNode = ({ id, data, type }) => {
  const schema = data?.schema;
  const updateNodeField = useStore(state => state.updateNodeField); 
  const [nodeData, setNodeData] = useState({});
  
  // Dynamic handles for Text node variable parsing
  const dynamicHandles = useDynamicHandles(schema, nodeData);

  const IconComponent = NODE_ICONS[schema?.icon];

  // Initialize field values with defaults
  useEffect(() => {
    const initialData = {};
    
    schema.fields?.forEach((field) => {
      if (nodeData[field.name] === undefined) {
        if (typeof field.default === 'function') {
          initialData[field.name] = field.default(id);
        } else {
          initialData[field.name] = field.default || '';
        }
      }
    });

    if (Object.keys(initialData).length > 0) {
      setNodeData(prevData => ({ ...prevData, ...initialData }));
      // Sync with global store
      Object.entries(initialData).forEach(([fieldName, value]) => {
        updateNodeField(id, fieldName, value);
      });
    }
  }, [id, schema.fields]);

  if (!schema) {
    return (
      <div className="px-5 py-4 w-80 border-2 border-red-500 bg-red-50 rounded-lg">
        <span className="text-red-600">Error: No schema provided</span>
      </div>
    );
  }

  const handleInputChange = (fieldName, value) => {
    setNodeData(prevData => ({
      ...prevData,
      [fieldName]: value,
    }));
    // Sync with global store
    updateNodeField(id, fieldName, value);
  };

  // Determine input handles (static or dynamic)
  const inputHandles = dynamicHandles.inputs.length > 0
    ? dynamicHandles.inputs
    : Array.isArray(schema.handles?.inputs)
      ? schema.handles.inputs
      : [];

  
  const outputHandles = schema.handles?.outputs || [];

  // Style variants
  const variantStyles = {
    input: 'border-blue-500 bg-blue-50',
    output: 'border-green-500 bg-green-50',
    processor: 'border-purple-500 bg-purple-50',
    transform: 'border-orange-500 bg-orange-50',
    utility: 'border-pink-500 bg-pink-50'
  };

  const variant = schema.style?.variant || 'input';
  const nodeClasses = variantStyles[variant] || variantStyles.input;

  return (
    <div
      className={`relative px-5 py-4 w-80 border-2 shadow-lg rounded-lg transition-all hover:shadow-xl ${nodeClasses}`}
      style={{ minHeight: '120px' }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        {IconComponent && (
          <span className="text-xl" style={{ color: schema.style?.color }}>
            <IconComponent />
          </span>
        )}
        <span className="font-semibold text-lg" style={{ color: schema.style?.color }}>
          {schema.label}
        </span>
      </div>

      {/* Description (optional) */}
      {schema.description && (
        <div className="text-xs text-gray-600 mb-3 italic">
          {schema.description}
        </div>
      )}

      {/* Custom Fields */}
      <div className="flex flex-col gap-3">
        {schema.fields?.map((field, index) => (
          <FieldRenderer
            key={`${id}-field-${index}`}
            field={field}
            value={nodeData[field.name]}
            onChange={handleInputChange}
            label={field.label}
          />
        ))}
      </div>

      {/* Input Handles */}
      {inputHandles.map((handle, index) => (
        <Handle
          key={`${id}-input-${handle.id || index}`}
          type="target"
          position={Position.Left}
          id={handle.id}
          style={{
            top: handle.position ? `${handle.position}%` : '50%',
            left: -6,
            background: '#fff',
            width: '12px',
            height: '12px',
            border: `2px solid ${schema.style?.color || '#3b82f6'}`,
          }}
          title={handle.label}
        />
      ))}

      {/* Output Handles */}
      {outputHandles.map((handle, index) => (
        <Handle
          key={`${id}-output-${handle.id || index}`}
          type="source"
          position={Position.Right}
          id={handle.id}
          style={{
            top: handle.position ? `${handle.position}%` : '50%',
            right: -6,
            background: '#fff',
            width: '12px',
            height: '12px',
            border: `2px solid ${schema.style?.color || '#3b82f6'}`,
          }}
          title={handle.label}
        />
      ))}
    </div>
  );
};