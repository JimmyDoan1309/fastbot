import React, { memo, useCallback, Dispatch, FC } from "react";
import {
  useZoomPanHelper,
  OnLoadParams,
  Elements,
  // FlowExportObject,
  isNode,
} from "react-flow-renderer";
// import localforage from "localforage";
import "./save.css";
import { saveBotDataAPI, getBotByIdAPI } from "../services/data-flow-services";

// localforage.config({
//   name: "react-flow",
//   storeName: "flows",
// });

// const flowKey = "example-flow";

type ControlsProps = {
  rfInstance?: OnLoadParams;
  setElements: Dispatch<React.SetStateAction<Elements<any>>>;
};

const SaveRestore: FC<ControlsProps> = ({ rfInstance, setElements }) => {
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
      saveBotDataAPI("20d11f9a-b313-44fc-9ab8-9e6b1ff3479c", newFlow);
      // localforage.setItem(flowKey, newFlow);
    }
  }, [rfInstance]);

  const onRestore = useCallback(() => {
    const restoreFlow = async () => {
      const botInfo = await getBotByIdAPI(
        "20d11f9a-b313-44fc-9ab8-9e6b1ff3479c"
      );
      let flow;
      if (botInfo) {
        flow = botInfo.data;
      }

      if (flow) {
        const [x = 0, y = 0] = flow.position;
        setElements(flow.elements || []);
        transform({ x, y, zoom: flow.zoom || 0 });
      }
    };

    restoreFlow();
  }, [setElements, transform]);

  return (
    <div className="save__controls">
      <button onClick={onSave}>save</button>
      <button onClick={onRestore}>restore</button>
    </div>
  );
};

export default memo(SaveRestore);
