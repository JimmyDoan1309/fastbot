import {
  FormControl,
  IconButton,
  Input,
  InputLabel,
  Typography,
} from "@material-ui/core";
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import { makeStyles } from "@material-ui/core/styles";
import { AddCircle } from "@material-ui/icons";
import React from "react";

interface Props {
  handleSubmit: (
    event: React.FormEvent<HTMLFormElement>,
    name: string,
    avatarUrl: string
  ) => void;
}

const useStyles = makeStyles({
  root: {
    width: 350,
    height: 250,
    margin: "0 auto",
    marginTop: "20px",
  },
  media: {
    height: "100%",
  },
});

const MediaCard: React.FC<Props> = ({ handleSubmit }) => {
  const classes = useStyles();

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
      <Card className={classes.root}>
        <form onSubmit={handleSubmitChild} style={{ padding: 15 }}>
          <Typography gutterBottom variant="h5" component="h2" align="center">
            Create Bot
          </Typography>
          <Typography gutterBottom variant="body2" component="body">
            Information:
          </Typography>
          <FormControl style={{ width: "100%" }}>
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
          <FormControl style={{ width: "100%" }}>
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
            style={{ display: "block", margin: "0 auto", marginTop: 20 }}
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
      <Card className={classes.root}>
        <IconButton style={{ height: "100%", width: "100%" }}>
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
