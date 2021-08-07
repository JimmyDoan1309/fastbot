import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import CardMedia from "@material-ui/core/CardMedia";
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
    maxWidth: 345,
    margin: "0 auto",
    marginTop: "20px",
  },
  media: {
    height: 200,
  },
});

const MediaCard: React.FC<Props> = ({ bot, handleDelete }) => {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardMedia
          className={classes.media}
          image={bot.avatarUrl}
          title="Contemplative Reptile"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2" align="center">
            {bot.name}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button href={`/flow/${bot.botId}`} size="small" color="primary">
          View Flow
        </Button>
        <Button
          size="small"
          color="primary"
          onClick={() => handleDelete(bot.botId)}
        >
          Delete
        </Button>
      </CardActions>
    </Card>
  );
};

export default MediaCard;
