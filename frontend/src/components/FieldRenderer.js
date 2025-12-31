// frontend/src/components/FieldRenderer.js

import { useRef, useEffect } from 'react';

/**
 * FieldRenderer - Generic field component
 * 
 * Renders any field type based on schema configuration.
 * Supports: text, textarea, select, number, checkbox, color
 */
const FieldRenderer = ({ field, value, onChange, label }) => {
  const textareaRef = useRef(null);

  const handleChange = (e) => {
    const newValue = field.type === 'checkbox' 
      ? e.target.checked 
      : e.target.value;
    onChange(field.name, newValue);
  };

  // Auto-resize textarea based on content
  useEffect(() => {
    if (field.type === 'textarea' && textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [value, field.type]);

  const commonClasses = "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all";

  switch (field.type) {
    case 'text':
      return (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            {label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <input
            type="text"
            value={value || ''}
            onChange={handleChange}
            placeholder={field.placeholder}
            className={commonClasses}
            required={field.required}
          />
        </div>
      );

    case 'textarea':
      return (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            {label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <textarea
            ref={textareaRef}
            value={value || ''}
            onChange={handleChange}
            placeholder={field.placeholder}
            rows={field.rows || 3}
            className={`${commonClasses} resize-none overflow-hidden`}
            required={field.required}
            style={{ minHeight: '60px' }}
          />
        </div>
      );

    case 'select':
      return (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            {label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <select
            value={value || field.default}
            onChange={handleChange}
            className={commonClasses}
            required={field.required}
          >
            {field.options?.map((option, index) => (
              <option key={index} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      );

    case 'number':
      return (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            {label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          <input
            type="number"
            value={value ?? field.default}
            onChange={handleChange}
            min={field.min}
            max={field.max}
            step={field.step}
            className={commonClasses}
            required={field.required}
          />
        </div>
      );

    case 'checkbox':
      return (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={value ?? field.default}
            onChange={handleChange}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <label className="text-sm font-medium text-gray-700">
            {label}
          </label>
        </div>
      );

    case 'color':
      return (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            {label}
          </label>
          <input
            type="color"
            value={value || field.default}
            onChange={handleChange}
            className="w-full h-10 rounded-md cursor-pointer"
          />
        </div>
      );

    default:
      return (
        <div className="text-sm text-red-500">
          Unsupported field type: {field.type}
        </div>
      );
  }
};

export default FieldRenderer;