import {
  FormControl,
  IconButton,
  Input,
  InputLabel,
  Typography,
} from "@material-ui/core";
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import { AddCircle } from "@material-ui/icons";
import React from "react";
import "./index.scss";

interface Props {
  handleSubmit: (
    event: React.FormEvent<HTMLFormElement>,
    name: string,
    avatarUrl: string
  ) => void;
}

const MediaCard: React.FC<Props> = ({ handleSubmit }) => {
  const [name, setName] = React.useState("");
  const [avatarUrl, setAvatarUrl] = React.useState(
    "http://www.chiemtaimobile.vn/images/Xiaomi/Xiaomi%20kh%C3%A1c/robot%20Xiaodan/robot.jpg?1530246679505"
  );
  const [toggle, setToggle] = React.useState(false);

  const handleSubmitChild = (event: React.FormEvent<HTMLFormElement>) => {
    handleSubmit(event, name, avatarUrl);
    setToggle(false);
    setName("");
    setAvatarUrl("");
  };

  const renderCreateForm = () => {
    return (
      <Card className="create-card">
        <form onSubmit={handleSubmitChild} className="form">
          <Typography gutterBottom variant="h5" component="h2" align="center">
            Create Bot
          </Typography>
          <Typography gutterBottom variant="body2" component="body">
            Information:
          </Typography>
          <FormControl className="form-control">
            <InputLabel htmlFor="my-input-name">Name</InputLabel>
            <Input
              id="my-input-name"
              aria-describedby="my-helper-text"
              value={name}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                setName(event.target.value)
              }
            />
          </FormControl>
          <FormControl className="form-control">
            <InputLabel htmlFor="my-input-avatar-url">Avatar URL</InputLabel>
            <Input
              id="my-input-avatar-url"
              aria-describedby="my-helper-text"
              value={avatarUrl}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                setAvatarUrl(event.target.value)
              }
            />
          </FormControl>
          <Button
            type="submit"
            className="button"
            color="primary"
            variant="contained"
          >
            CREATE
          </Button>
        </form>
      </Card>
    );
  };

  if (toggle) {
    return renderCreateForm();
  } else {
    return (
      <Card className="create-card">
        <IconButton className="icon-button">
          <AddCircle
            style={{ fontSize: 100 }}
            onClick={() => setToggle(!toggle)}
          />
        </IconButton>
      </Card>
    );
  }
};

export default MediaCard;
