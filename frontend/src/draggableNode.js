export const DraggableNode = ({ type, label, icon }) => {
  const onDragStart = (event) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({ nodeType: type })
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div
      draggable
      onDragStart={onDragStart}
      className="
        group cursor-grab active:cursor-grabbing
        rounded-lg border border-gray-200
        bg-white px-3 py-3
        flex flex-col items-center justify-center gap-2
        transition-all duration-150
        hover:shadow-md hover:border-blue-400
      "
    >
      <div
        className="
          text-xl text-gray-600
          group-hover:text-blue-500
          transition-colors
        "
      >
        {icon}
      </div>

      <div className="text-xs font-medium text-gray-700 text-center">
        {label}
      </div>
    </div>
  );
};
