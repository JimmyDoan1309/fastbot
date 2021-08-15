import React, { Dispatch, FC, memo, useCallback, useEffect } from "react";
import { Elements, OnLoadParams, useZoomPanHelper } from "react-flow-renderer";
import {
  getBotByIdAPI,
  saveBotDataAPI,
} from "../../services/data-flow-services";
import "./save.css";

type ControlsProps = {
  id: string;
  rfInstance?: OnLoadParams;
  setElements: Dispatch<React.SetStateAction<Elements<any>>>;
};

const SaveRestore: FC<ControlsProps> = ({ id, rfInstance, setElements }) => {
  const { transform } = useZoomPanHelper();

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

  useEffect(() => {
    onRestore();
  }, [id, onRestore]);

  const onSave = useCallback(() => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      saveBotDataAPI(id, flow);
    }
  }, [id, rfInstance]);

  return (
    <div className="save__controls">
      <button onClick={onSave}>save</button>
      <button onClick={onRestore}>restore</button>
    </div>
  );
};

export default memo(SaveRestore);
