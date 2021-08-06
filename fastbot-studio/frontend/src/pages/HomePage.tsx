import {
  Button,
  FormControl,
  Input,
  InputLabel,
  List,
  ListItem,
  Modal,
} from "@material-ui/core";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import React, { useEffect, useState } from "react";
import {
  Link as RouterLink,
  LinkProps as RouterLinkProps,
} from "react-router-dom";
import BotInfo from "../components/BotInfo";
import Bot from "../inferfaces/Bot";
import { createBotsAPI, getAllBotsAPI } from "../services/data-flow-services";

interface ListItemLinkProps {
  icon?: React.ReactElement;
  primary?: string;
  to: string;
}

interface CreateBot {
  timezone: string;
  name: string;
  language: string;
  avatarUrl: string;
}

const ListItemLink: React.FC<ListItemLinkProps> = ({
  icon,
  primary,
  to,
  children,
}) => {
  const renderLink = React.useMemo(
    () =>
      React.forwardRef<any, Omit<RouterLinkProps, "to">>((itemProps, ref) => (
        <RouterLink to={to} ref={ref} {...itemProps} />
      )),
    [to]
  );

  return (
    <li>
      <ListItem button component={renderLink}>
        {children}
      </ListItem>
    </li>
  );
};

const HomePage = () => {
  const [bots, setBot] = useState<Bot[]>();
  const [open, setOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [avatarUrl, setAvatarUrl] = React.useState("");
  const classes = useStyles();

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const getAllBots = async () => {
    const result = await getAllBotsAPI();
    if (result) {
      setBot(result as unknown as Bot[]);
    }
  };

  useEffect(() => {
    getAllBots();
  }, []);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const createBotInfo: CreateBot = {
      timezone: "UTC",
      name,
      language: "en",
      avatarUrl,
    };
    const result = await createBotsAPI(createBotInfo);
    if (result) {
      handleClose();
    }
  };

  return (
    <React.Fragment>
      <Button
        variant="outlined"
        color="primary"
        style={{ margin: "0 auto", display: "block" }}
        onClick={handleOpen}
      >
        Create Bot
      </Button>

      <List>
        {bots?.map((bot) => (
          <ListItemLink to={`/flow/${bot.botId}`} key={bot.botId}>
            <BotInfo bot={bot} />
          </ListItemLink>
        ))}
      </List>

      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="simple-modal-title"
        aria-describedby="simple-modal-description"
        className={classes.modal}
      >
        <div className={classes.paper}>
          <h2 id="simple-modal-title">Create New Bot</h2>
          <p id="simple-modal-description">Information:</p>
          <form onSubmit={handleSubmit}>
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
        </div>
      </Modal>
    </React.Fragment>
  );
};

export default HomePage;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    modal: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    paper: {
      backgroundColor: theme.palette.background.paper,
      border: "2px solid #000",
      boxShadow: theme.shadows[5],
      padding: theme.spacing(2, 4, 3),
    },
  })
);
