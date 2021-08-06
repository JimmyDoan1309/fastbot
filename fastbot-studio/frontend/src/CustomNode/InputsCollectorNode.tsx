import React, { memo, FC, CSSProperties, useState } from "react";

import {
  Handle,
  Position,
  NodeProps,
  Connection,
  Edge,
} from "react-flow-renderer";

const targetHandleStyle: CSSProperties = { background: "#555" };
const sourceHandleStyle: CSSProperties = { ...targetHandleStyle };

const onConnect = (params: Connection | Edge) =>
  console.log("handle onConnect", params);

const ColorSelectorNode: FC<NodeProps> = ({ data, isConnectable }) => {
  const [toggle, setToggle] = useState(true);
  const [name, setName] = useState(data.label);

  React.useEffect(() => {
    setName(data.label);
  }, [data.label]);

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        style={targetHandleStyle}
        onConnect={onConnect}
      />
      {toggle ? (
        <p
          onDoubleClick={() => {
            setToggle(false);
          }}
        >
          {name}
        </p>
      ) : (
        <input
          type="text"
          value={name}
          style={{
            width: 150,
            border: "1px solid",
            margin: "0 auto",
            padding: 0,
          }}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
            setName(event.target.value);
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === "Escape") {
              setToggle(true);
              data.onChange(data.id, name);
              event.preventDefault();
              event.stopPropagation();
            }
          }}
        />
      )}
      <Handle
        type="source"
        position={Position.Bottom}
        id="a"
        style={sourceHandleStyle}
        isConnectable={isConnectable}
      />
    </>
  );
};

export default memo(ColorSelectorNode);
