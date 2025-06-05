import React, { useState, useEffect } from "react";
import ForgeReconciler, { Text, Button, useProductContext } from "@forge/react";
import { invoke } from "@forge/bridge";

const App = () => {
  const [status, setStatus] = useState("idle");
  const context = useProductContext();

  useEffect(() => {
    const generate = async () => {
      if (!context?.content?.id) return;
      // const pageId = context.content.id;
      const pageId = 66354;
      console.log("Extracted pageId:", pageId);
      await invoke("gpt-resolver", { pageId });
    };
    generate();
  }, [context]);

  const handleClick = async () => {
    setStatus("loading");
    console.log("Context:", context);

    try {
      // const pageId = context?.extension?.content?.id;
      const pageId = 66354;
      console.log("Extracted pageId:", pageId);

      const result = await invoke("gpt-resolver", { pageId });
      setStatus("success");
    } catch (err) {
      console.error("Error invoking resolver:", err);
      setStatus("error");
    }
  };

  return (
    <>
      <Text>
        Click to generate a structured breakdown of this page’s requirements.
      </Text>
      <Button appearance="primary" onClick={handleClick}>
        Generate Breakdown
      </Button>

      {status === "loading" && <Text>Generating breakdown…</Text>}
      {status === "success" && <Text>✅ New page created with table.</Text>}
      {status === "error" && <Text>❌ Failed to create breakdown.</Text>}
    </>
  );
};

ForgeReconciler.render(<App />);
