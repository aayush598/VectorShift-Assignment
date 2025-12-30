import { PipelineToolbar } from "./toolbar";
import { PipelineUI } from "./ui";
import { SubmitButton } from "./submit";

function App() {
  return (
    <div className="flex h-screen">
      <PipelineToolbar />
      <div className="flex-1">
        <PipelineUI />
        <SubmitButton />
      </div>
    </div>
  );
}

export default App;
