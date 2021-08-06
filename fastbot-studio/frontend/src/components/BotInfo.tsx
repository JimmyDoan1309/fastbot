import React from "react";
import Bot from "../inferfaces/Bot";

interface Props {
  bot: Bot;
}

const BotInfo: React.FC<Props> = ({ bot }) => {
  return (
    <div>
      <p>{bot.name}</p>
    </div>
  );
};

export default BotInfo;
