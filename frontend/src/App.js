import { PipelineToolbar } from "./toolbar";
import { PipelineUI } from "./ui";
import { SubmitButton } from "./submit";
import { BackendStatusBanner } from "./components/BackendStatusBanner";
import { Bounce, ToastContainer } from "react-toastify";

function App() {
  return (
    <div className="relative w-screen h-screen overflow-hidden bg-gray-50">
      {/* Canvas Area - Full screen */}
      <PipelineUI />

      {/* Overlay UI Layer */}
      <div className="pointer-events-none absolute inset-0 z-10 flex flex-col justify-between">
        {/* Top Overlay */}
        <div className="pointer-events-auto flex flex-col">
          {/* Backend Status */}
          <BackendStatusBanner />

          {/* Toolbar */}
          <PipelineToolbar />
        </div>

        {/* Bottom Overlay */}
        <div className="pointer-events-auto absolute bottom-6 left-1/2 -translate-x-1/2">
          <SubmitButton />
        </div>
      </div>

      {/* Toasts */}
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
