import { Button, TextField } from "@material-ui/core";
import React from "react";
import { Node } from "react-flow-renderer";

interface Props {
  node: Node;
}

const SelectedElementConfig: React.FC<Props> = ({ node }) => {
  const [label, setLabel] = React.useState(node.data.label);

  React.useEffect(() => {
    setLabel(node.data.label);
  }, [node]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLabel(event.target.value);
  };

  const handleSave = () => {
    node.data.onChange(node.id, label);
  };

  return (
    <aside className="leftAside">
      <div className="title">Node Config</div>
      <div className="text-field">
        <TextField
          size="small"
          id="outlined-label"
          label="Label"
          variant="outlined"
          value={label}
          onChange={handleChange}
        />
      </div>
      <Button
        variant="contained"
        fullWidth
        color="primary"
        onClick={handleSave}
      >
        Save
      </Button>
    </aside>
  );
};

export default SelectedElementConfig;
