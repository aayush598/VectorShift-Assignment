import { PipelineToolbar } from "./toolbar";
import { PipelineUI } from "./ui";
import { SubmitButton } from "./submit";
import { Bounce, ToastContainer } from "react-toastify";

function App() {
  return (
    <div className="relative w-screen h-screen overflow-hidden bg-gray-50">
      {/* Canvas Area - Now full screen */}
      <PipelineUI />

      {/* Overlay UI Layer */}
      <div className="pointer-events-none absolute inset-0 z-10 flex flex-col justify-between p-4">
        {/* Top Overlay: Toolbar */}
        <div className="pointer-events-auto">
          <PipelineToolbar />
        </div>

        {/* Bottom Overlay: Submit Button */}
        <div className="pointer-events-auto absolute bottom-6 left-1/2 -translate-x-1/2">
          <SubmitButton />
        </div>
      </div>

      <ToastContainer
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
        transition={Bounce}
      />
    </div>
  );
}

export default App;