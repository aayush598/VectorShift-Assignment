import { useMemo, useState } from "react";
import { DraggableNode } from "./draggableNode";
import { getToolbarNodesByCategory } from "./config/toolbarRegistry";
import { NODE_ICONS } from "./config/nodeIcons";
import { CiSearch } from "react-icons/ci";

export const PipelineToolbar = () => {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState(null);

  const toolbarGroups = getToolbarNodesByCategory();
  const categories = Object.keys(toolbarGroups);

  // Default to first category
  const selectedCategory = activeCategory || categories[0];

  const filteredNodes = useMemo(() => {
    return toolbarGroups[selectedCategory].filter((node) =>
      node.label.toLowerCase().includes(search.toLowerCase())
    );
  }, [toolbarGroups, selectedCategory, search]);

  return (
    <header className="w-full border-b border-gray-200 bg-white">
      {/* Top Bar */}
      <div className="flex items-center gap-4 px-6 py-3">
        {/* Search */}
        <div className="relative w-64">
          <CiSearch
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />

          <input
            type="text"
            placeholder="Search nodes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="
              w-full pl-9 pr-3 py-2 text-sm
              border border-gray-300 rounded-md
              focus:outline-none focus:ring-2 focus:ring-blue-500
            "
          />
        </div>

        

        {/* Categories */}
        <div className="flex gap-6 items-center">
          {categories.map((category) => {
            const isActive = category === selectedCategory;

            return (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`
                  text-sm font-medium
                  pb-1
                  transition-colors
                  ${
                    isActive
                      ? "text-[#6366f1] border-b-2 border-[#6366f1]"
                      : "text-gray-600 border-b-2 border-transparent hover:text-[#6366f1]"
                  }
                `}
              >
                {category}
              </button>
            );
          })}
        </div>

      </div>

      {/* Node Grid */}
      <div className="px-6 py-4">
        {filteredNodes.length === 0 ? (
          <div className="text-sm text-gray-500">
            No nodes found in this category.
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-4">
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
        )}
      </div>
    </header>
  );
};
