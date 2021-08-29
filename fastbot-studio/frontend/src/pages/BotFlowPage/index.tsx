import React, { DragEvent, MouseEvent, useState } from "react";
import ReactFlow, {
  addEdge,
  ArrowHeadType,
  Background,
  BackgroundVariant,
  Connection,
  Controls,
  Edge,
  ElementId,
  Elements,
  FlowElement,
  isEdge,
  isNode,
  Node,
  OnLoadParams,
  ReactFlowProvider,
  removeElements,
} from "react-flow-renderer";
import { useParams } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import ConfigNodePanel from "../../components/ConfigNodePanel";
import SaveAndRestore from "../../components/SaveAndRestore";
import {
  InputsCollectorNode,
  IntentNode,
  ProcessNode,
  ResponseNode,
} from "../../CustomNode";
import "./dnd.css";
import Sidebar from "./Sidebar";

const DELETE_KEY = 46;
const initialElements: any[] = [];

const nodeTypes = {
  intent: IntentNode,
  inputsCollector: InputsCollectorNode,
  process: ProcessNode,
  response: ResponseNode,
};

type Params = {
  id: string;
};

const onDragOver = (event: DragEvent) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
};

const getId = (): ElementId => uuidv4();

const DnDFlow = () => {
  let { id } = useParams<Params>();
  const [reactFlowInstance, setReactFlowInstance] = useState<OnLoadParams>();
  const [totalElements, setElements] = useState<Elements>(initialElements);
  const [selectedElement, setSelectedElement] = useState<FlowElement | null>();

  const onChange = (id: string, newLable: string) => {
    const updateElements = totalElements.map((element) => {
      if (element.id === id) {
        element.data.label = newLable;
      }
      return element;
    });
    setElements(updateElements);
  };

  const onAddNewSample = (id: string, newSample: string) => {
    const updateElements = totalElements.map((element) => {
      if (element.id === id) {
        if (!element.data.samples) {
          element.data.samples = [];
        }
        element.data.samples = [...element.data.samples, newSample];
        setSelectedElement(element);
      }
      return element;
    });
    setElements(updateElements);
  };

  const onDeleteSample = (id: string, sampleId: number) => {
    const tempTotalElement = totalElements.map((element) => {
      if (element.id === id) {
        (element.data.samples as string[]).splice(sampleId, 1);
      }
      return element;
    });
    setElements(tempTotalElement);
  };

  const convertArrowHead = (elements: Elements) => {
    return elements.map((element) => {
      if (isEdge(element)) {
        const edgeElement = element as Edge;
        element.arrowHeadType = ArrowHeadType.ArrowClosed;
        element.style = { strokeWidth: 3 };
        return edgeElement;
      } else {
        let nodeElement = element as Node;
        nodeElement = {
          ...element,
          style: {
            ...element.style,
            padding: "10px",
            borderRadius: "3px",
            width: "150px",
            fontSize: "14px",
            color: "#222",
            textAlign: "center",
            borderWidth: "2px",
            borderStyle: "solid",
            background: "#fff",
            borderColor:
              element.type === "intent"
                ? "blue"
                : element.type === "inputsCollector"
                ? "red"
                : element.type === "process"
                ? "orange"
                : "green",
          },
        };
        return nodeElement;
      }
    });
  };

  function capitalizeFirstLetter(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  const onConnect = (params: Connection | Edge) =>
    setElements((els) => {
      const edge = params as Edge;
      edge.arrowHeadType = ArrowHeadType.ArrowClosed;
      return addEdge(edge, els);
    });

  const onElementsRemove = (elementsToRemove: Elements) =>
    setElements((els) => removeElements(elementsToRemove, els));

  const onElementClick = (_: MouseEvent, element: FlowElement) => {
    setSelectedElement(element);
    setElements((els) =>
      els.map((el) => {
        if (el.id === element.id) {
          el.style = {
            ...el.style,
            boxShadow:
              "rgb(0 0 0 / 50%) 0px 4px 8px 0px, rgb(0 0 0 / 20%) 0px 6px 20px 0px",
          };
        } else {
          el.style = { ...el.style, boxShadow: "unset" };
        }
        return el;
      })
    );
  };

  const onPanelClick = () => {
    setSelectedElement(null);
    setElements((els) =>
      els.map((el) => {
        el.style = { ...el.style, boxShadow: "unset" };
        return el;
      })
    );
  };

  const onLoad = (_reactFlowInstance: OnLoadParams) =>
    setReactFlowInstance(_reactFlowInstance);

  const onDrop = (event: DragEvent) => {
    event.preventDefault();

    if (reactFlowInstance) {
      const type = event.dataTransfer.getData("application/reactflow");
      const position = reactFlowInstance.project({
        x: event.clientX,
        y: event.clientY,
      });
      const newId = getId();
      let newNode: Node;
      if (type === "intent" || type === "response") {
        newNode = {
          id: newId,
          type,
          position,
          data: {
            id: newId,
            label: `${capitalizeFirstLetter(type)} Node `,
            samples: [],
          },
        };
      } else {
        newNode = {
          id: newId,
          type,
          position,
          data: {
            id: newId,
            label: `${capitalizeFirstLetter(type)} Node `,
          },
        };
      }
      setElements((es) => es.concat(newNode));
    }
  };

  return (
    <div className="dndflow">
      <ReactFlowProvider>
        {/* Selected Element Properties */}
        {selectedElement && isNode(selectedElement) ? (
          <ConfigNodePanel
            node={selectedElement as Node}
            onChange={onChange}
            onAddNewSample={onAddNewSample}
            onDeleteSample={onDeleteSample}
          />
        ) : null}
        {/* Reactflow Wrapper */}
        <div className="reactflow-wrapper">
          <ReactFlow
            elements={convertArrowHead(totalElements)}
            onConnect={onConnect}
            onElementsRemove={onElementsRemove}
            onElementClick={onElementClick}
            elementsSelectable={true}
            onPaneClick={onPanelClick}
            deleteKeyCode={DELETE_KEY}
            onLoad={onLoad}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            className="full-screen"
          >
            <Controls />
            <SaveAndRestore
              id={id}
              rfInstance={reactFlowInstance}
              setElements={setElements}
            />
            <Background variant={BackgroundVariant.Dots} />
          </ReactFlow>
        </div>
        <Sidebar />
      </ReactFlowProvider>
    </div>
  );
};

export default DnDFlow;
