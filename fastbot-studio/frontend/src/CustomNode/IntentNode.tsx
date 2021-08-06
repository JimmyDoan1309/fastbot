import React, { CSSProperties, FC, memo, useState } from "react";
import { Handle, NodeProps, Position } from "react-flow-renderer";

const targetHandleStyle: CSSProperties = { background: "#555" };
const sourceHandleStyle: CSSProperties = { ...targetHandleStyle };

const IntentNode: FC<NodeProps> = ({ data, isConnectable }) => {
  const [toggle, setToggle] = useState(true);
  const [name, setName] = useState(data.label);

  React.useEffect(() => {
    setName(data.label);
  }, [data.label]);

  return (
    <>
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

export default memo(IntentNode);
