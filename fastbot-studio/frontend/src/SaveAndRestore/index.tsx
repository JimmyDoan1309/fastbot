import React, { Dispatch, FC, memo, useCallback } from "react";
import {
  Elements,
  // FlowExportObject,
  isNode,
  OnLoadParams,
  useZoomPanHelper,
} from "react-flow-renderer";
import { getBotByIdAPI, saveBotDataAPI } from "../services/data-flow-services";
// import localforage from "localforage";
import "./save.css";

// localforage.config({
//   name: "react-flow",
//   storeName: "flows",
// });

// const flowKey = "example-flow";

type ControlsProps = {
  id: string;
  rfInstance?: OnLoadParams;
  setElements: Dispatch<React.SetStateAction<Elements<any>>>;
};

const SaveRestore: FC<ControlsProps> = ({ id, rfInstance, setElements }) => {
  const { transform } = useZoomPanHelper();

  const onSave = useCallback(() => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      const newElements = flow.elements;
      newElements.map((element) => {
        if (isNode(element)) {
          element.data = {
            label: element.data.label,
          };
        }
        return element;
      });
      let newFlow = flow;
      newFlow.elements = newElements;
      saveBotDataAPI(id, newFlow);
      // localforage.setItem(flowKey, newFlow);
    }
  }, [id, rfInstance]);

  const onRestore = useCallback(() => {
    const restoreFlow = async () => {
      const botInfo = await getBotByIdAPI(id);
      let flow;
      if (botInfo) {
        flow = botInfo.data;
      }

      if (Object.keys(flow).length !== 0) {
        const [x = 0, y = 0] = flow.position;
        setElements(flow.elements || []);
        transform({ x, y, zoom: flow.zoom || 0 });
      }
    };

    restoreFlow();
  }, [id, setElements, transform]);

  return (
    <div className="save__controls">
      <button onClick={onSave}>save</button>
      <button onClick={onRestore}>restore</button>
    </div>
  );
};

export default memo(SaveRestore);
