import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-xcode";

interface Props {
  value: string;
  onChange: (newValue: string) => void;
}

const MyAceEditor: React.FC<Props> = ({ value, onChange }) => {
  return (
    <AceEditor
      placeholder="Placeholder Text"
      mode="python"
      theme="xcode"
      name="blah2"
      value={value}
      onChange={onChange}
      fontSize={14}
      showPrintMargin={true}
      showGutter={true}
      highlightActiveLine={true}
      width="100%"
    />
  );
};

export default MyAceEditor;
