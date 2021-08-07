import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Avatar from "@material-ui/core/Avatar";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React from "react";
import Bot from "../inferfaces/Bot";

interface Props {
  bot: Bot;
  handleDelete: (id: string) => void;
}

const useStyles = makeStyles({
  root: {
    width: 350,
    height: 250,
    margin: "0 auto",
    marginTop: "20px",
  },
  avatar: {
    height: 100,
    width: 100,
    fontSize: 50,
    fontWeight: "bold",
  },
  avatarDiv: {
    display: "flex",
    justifyContent: "center",
    marginTop: 20,
  },
  actions: {
    display: "flex",
    justifyContent: "space-between",
  },
  buttonsGroup: {
    "& > *": {
      marginRight: 5,
    },
  },
});

const MediaCard: React.FC<Props> = ({ bot, handleDelete }) => {
  const classes = useStyles();
  return (
    <Card className={classes.root}>
      <CardActionArea>
        <div className={classes.avatarDiv}>
          <Avatar src={bot.avatarUrl} className={classes.avatar}>
            {bot.name[0].toUpperCase()}
          </Avatar>
        </div>

        <CardContent>
          <Typography gutterBottom variant="h5" component="h2" align="center">
            {bot.name}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions className={classes.actions}>
        <div className={classes.buttonsGroup}>
          <Button
            href={`/bot/${bot.botId}/workflow`}
            size="small"
            color="primary"
          >
            Edit
          </Button>
          <Button size="small" color="primary">
            Download
          </Button>
        </div>
        <Button
          size="small"
          color="secondary"
          onClick={() => handleDelete(bot.botId)}
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
};

export default MediaCard;
