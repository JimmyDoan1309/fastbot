import {
  Button,
  IconButton,
  TextField,
  Grid,
  Tooltip,
} from "@material-ui/core";
import AddIcon from "@material-ui/icons/Add";
import RemoveIcon from "@material-ui/icons/Remove";
import React, { useState } from "react";
import { Node } from "react-flow-renderer";
import MyAceEditor from "../MyAceEditor";
import "./index.css";

interface Props {
  node: Node;
  onChange: (id: string, newLabel: string) => void;
  onAddNewSample: (id: string, newSample: string) => void;
  onDeleteSample: (id: string, sampleId: number) => void;
  onSaveProcessNode: (
    id: string,
    newLabel: string,
    codeEditorValue: string
  ) => void;
}

interface SampleProps {
  nodeId: string;
  sampleId: number;
  text: string;
  onDeleteSample: (id: string, sampleId: number) => void;
}

const SampleItem: React.FC<SampleProps> = ({
  nodeId,
  sampleId,
  text,
  onDeleteSample,
}) => {
  const handleDelete = () => {
    onDeleteSample(nodeId, sampleId);
  };

  return (
    <div>
      <Tooltip title="Delete">
        <IconButton aria-label="delete" size="small" onClick={handleDelete}>
          <RemoveIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <span>{text}</span>
    </div>
  );
};

const SelectedElementConfig: React.FC<Props> = ({
  node,
  onChange,
  onAddNewSample,
  onDeleteSample,
  onSaveProcessNode,
}) => {
  const [label, setLabel] = useState(node.data.label);
  const [newSample, setNewSample] = useState("");
  const [codeEditorValue, setCodeEditorValue] = useState("");

  React.useEffect(() => {
    setLabel(node.data.label);
    if (node.data.codeEditorValue) {
      setCodeEditorValue(node.data.codeEditorValue);
    }
  }, [node]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLabel(event.target.value);
  };

  const handleAddNewSample = () => {
    setNewSample("");
    onAddNewSample(node.id, newSample);
  };

  const handleChangeCodeEditor = (newValue: string) => {
    setCodeEditorValue(newValue);
  };

  const handleSave = () => {
    if (node.type !== "process") {
      onChange(node.id, label);
    } else {
      onSaveProcessNode(node.id, label, codeEditorValue);
    }
  };

  return (
    <aside className="left-aside config-left-aside">
      <div className="title">Node Config</div>
      <div>
        <TextField
          size="small"
          label="Label"
          variant="outlined"
          value={label}
          className="text-field"
          onChange={handleChange}
        />
      </div>
      {node.type === "intent" || node.type === "response" ? (
        <React.Fragment>
          <div className="sample">Samples</div>
          <div className="sample-list">
            {node.data.samples &&
              (node.data.samples as string[]).map((item, index) => (
                <SampleItem
                  key={index}
                  nodeId={node.id}
                  sampleId={index}
                  text={item}
                  onDeleteSample={onDeleteSample}
                />
              ))}
          </div>
          <div className="new-sample">
            <Grid container spacing={1} alignItems="flex-end">
              <Grid item>
                <Tooltip title="Add New Sample">
                  <IconButton
                    aria-label="add"
                    size="small"
                    onClick={handleAddNewSample}
                  >
                    <AddIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Grid>
              <Grid item>
                <TextField
                  id="input-with-icon-grid"
                  label="New Sample"
                  size="small"
                  value={newSample}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                    setNewSample(event.target.value)
                  }
                />
              </Grid>
            </Grid>
          </div>
        </React.Fragment>
      ) : null}
      {node.type === "process" ? (
        <MyAceEditor
          value={codeEditorValue}
          onChange={handleChangeCodeEditor}
        />
      ) : null}
      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={handleSave}
      >
        Save
      </Button>
    </aside>
  );
};

export default SelectedElementConfig;
