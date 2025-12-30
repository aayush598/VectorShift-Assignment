import { nodeSchemas } from "./nodeSchema";

/**
 * Returns toolbar nodes grouped by category
 */
export const getToolbarNodes = () => {
  return Object.values(nodeSchemas)
    .filter(schema => schema.showInToolbar)
    .sort((a, b) => (a.toolbarOrder ?? 0) - (b.toolbarOrder ?? 0));
};

/**
 * Group nodes by category for sectioned toolbar
 */
export const getToolbarNodesByCategory = () => {
  return getToolbarNodes().reduce((acc, schema) => {
    const category = schema.category || "other";
    if (!acc[category]) acc[category] = [];
    acc[category].push(schema);
    return acc;
  }, {});
};
