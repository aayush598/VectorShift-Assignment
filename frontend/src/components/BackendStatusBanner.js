import { useBackendStatus } from "../hooks/useBackendStatus";

export const BackendStatusBanner = () => {
  const { isConnected } = useBackendStatus();

  if (isConnected === null) {
    return (
      <div className="w-full bg-gray-100 text-gray-700 text-sm px-4 py-2 text-center">
        Checking backend status…
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="w-full bg-red-100 text-red-700 text-sm px-4 py-2 text-center">
        Backend disconnected. Retrying connection…
      </div>
    );
  }

  return (
    <div className="w-full bg-green-100 text-green-700 text-sm px-4 py-2 text-center">
      Backend connected ✓
    </div>
  );
};
