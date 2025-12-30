import { useState } from "react";
import { DraggableNode } from "./draggableNode";
import { getToolbarNodesByCategory } from "./config/toolbarRegistry";
import { NODE_ICONS } from "./config/nodeIcons";

export const PipelineToolbar = () => {
  const [search, setSearch] = useState("");
  const toolbarGroups = getToolbarNodesByCategory();

  return (
    <aside className="w-72 h-screen bg-gray-50 border-r border-gray-200 flex flex-col">
      
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Nodes</h2>
        <p className="text-xs text-gray-500 mt-1">
          Drag nodes onto the canvas
        </p>
      </div>

      {/* Search */}
      <div className="px-4 py-3 border-b border-gray-200">
        <input
          type="text"
          placeholder="Search nodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="
            w-full px-3 py-2 text-sm
            border border-gray-300 rounded-md
            focus:outline-none focus:ring-2 focus:ring-blue-500
            bg-white
          "
        />
      </div>

      {/* Node List */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {Object.entries(toolbarGroups).map(([category, nodes]) => {
          const filteredNodes = nodes.filter((node) =>
            node.label.toLowerCase().includes(search.toLowerCase())
          );

          if (filteredNodes.length === 0) return null;

          return (
            <section key={category}>
              <div className="mb-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                {category}
              </div>

              <div className="grid grid-cols-2 gap-3">
                {filteredNodes.map((node) => {
                  const Icon = NODE_ICONS[node.icon];

                  return (
                    <DraggableNode
                      key={node.type}
                      type={node.type}
                      label={node.label}
                      icon={Icon ? <Icon /> : null}
                    />
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>
    </aside>
  );
};
