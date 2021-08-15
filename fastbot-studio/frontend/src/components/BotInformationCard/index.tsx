import Avatar from "@material-ui/core/Avatar";
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import React from "react";
import Bot from "../../inferfaces/Bot";
import "./index.scss";

interface Props {
  bot: Bot;
  handleDelete: (id: string) => void;
}

const BotInformationCard: React.FC<Props> = ({ bot, handleDelete }) => {
  return (
    <Card className="bot-card">
      <CardActionArea>
        <div className="avatar-div">
          <Avatar src={bot.avatarUrl} className="avatar">
            {bot.name[0].toUpperCase()}
          </Avatar>
        </div>

        <CardContent>
          <Typography gutterBottom variant="h5" component="h2" align="center">
            {bot.name}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions className="actions">
        <div className="buttons-group">
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

export default BotInformationCard;
