import { Bounce, toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useStore } from "./store";
import { shallow } from "zustand/shallow";
import { Button } from "@nextui-org/react";
import { getNodeSchema } from "./config/nodeSchema";

export const SubmitButton = () => {
  const { nodes, edges } = useStore(
    (state) => ({
      nodes: state.nodes,
      edges: state.edges,
    }),
    shallow
  );

  const validateNodes = () => {
    const invalidNodes = nodes.filter(node => {
      const schema = getNodeSchema(node.type);
      if (!schema) return false;
      
      return schema.fields?.some(field => {
        if (field.required) {
          const value = node.data?.[field.name];
          return value === undefined || value === null || value === '';
        }
        return false;
      });
    });

    return invalidNodes;
  };

  const handleSubmit = async () => {
    // Validate required fields
    const invalidNodes = validateNodes();
    if (invalidNodes.length > 0) {
      toast.error(
        <div className="flex flex-col gap-1">
          <b>Validation Error</b>
          <span>Some nodes have missing required fields</span>
          <span className="text-xs mt-1">
            {invalidNodes.length} node(s) need attention
          </span>
        </div>,
        {
          position: "top-center",
          autoClose: 4000,
          theme: "dark",
          transition: Bounce,
        }
      );
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/pipelines/parse",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ nodes, edges }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Server error');
      }

      const result = await response.json();

      // Show different message based on DAG status
      const toastContent = (
        <div className="flex flex-col p-1 text-base gap-1">
          <span>
            <b>Nodes:</b> {result.num_nodes}
          </span>
          <span>
            <b>Edges:</b> {result.num_edges}
          </span>
          <span>
            <b>Is DAG:</b> {result.is_dag ? "✓ Yes" : "✗ No"}
          </span>
          {result.cache_hit && (
            <span className="text-xs text-gray-400 mt-1">
              (Cached result)
            </span>
          )}
        </div>
      );

      if (result.is_dag) {
        toast.success(toastContent, {
          position: "top-center",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          theme: "dark",
          transition: Bounce,
        });
      } else {
        toast.warning(toastContent, {
          position: "top-center",
          autoClose: 6000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          theme: "dark",
          transition: Bounce,
        });
      }
    } catch (error) {
      console.error("Error submitting the pipeline:", error);
      toast.error(
        <div className="flex flex-col gap-1">
          <b>Submission Failed</b>
          <span>{error.message || 'Please try again'}</span>
        </div>,
        {
          position: "top-center",
          autoClose: 5000,
          theme: "dark",
          transition: Bounce,
        }
      );
    }
  };

  return (
    <div className="flex items-center justify-center fixed bottom-10 left-0 right-0">
      <Button onClick={handleSubmit} color="primary" size="lg" type="submit">
        Submit Pipeline
      </Button>
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
};