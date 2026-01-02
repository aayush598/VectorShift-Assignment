import { PipelineToolbar } from "./toolbar";
import { PipelineUI } from "./ui";
import { SubmitButton } from "./submit";

function App() {
  return (
    <div className="flex flex-col h-screen">
      {/* Top Toolbar */}
      <PipelineToolbar />

      {/* Canvas Area */}
      <div className="flex-1 relative">
        <PipelineUI />
        <SubmitButton />
      </div>
    </div>
  );
}

export default App;
