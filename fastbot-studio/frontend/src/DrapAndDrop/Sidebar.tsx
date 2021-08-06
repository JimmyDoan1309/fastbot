import React, { DragEvent } from "react";

const onDragStart = (event: DragEvent, nodeType: string) => {
  event.dataTransfer.setData("application/reactflow", nodeType);
  event.dataTransfer.effectAllowed = "move";
};

const Sidebar = () => {
  return (
    <aside>
      <div className="description">
        You can drag these nodes to the pane on the left.
      </div>
      <div
        className="react-flow__node-input"
        onDragStart={(event: DragEvent) => onDragStart(event, "intent")}
        draggable
      >
        Intent
      </div>
      <div
        className="react-flow__node-default"
        onDragStart={(event: DragEvent) =>
          onDragStart(event, "inputsCollector")
        }
        draggable
      >
        InputsCollector
      </div>
      <div
        className="react-flow__node-default"
        onDragStart={(event: DragEvent) => onDragStart(event, "process")}
        draggable
      >
        Process
      </div>
      <div
        className="react-flow__node-output"
        onDragStart={(event: DragEvent) => onDragStart(event, "response")}
        draggable
      >
        Response
      </div>
    </aside>
  );
};

export default Sidebar;
