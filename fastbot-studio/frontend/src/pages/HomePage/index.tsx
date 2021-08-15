import { Grid } from "@material-ui/core";
import React, { useEffect, useState } from "react";
import BotInformationCard from "../../components/BotInformationCard";
import CreateBotCard from "../../components/CreateBotCard";
import Bot from "../../inferfaces/Bot";
import {
  createBotsAPI,
  deleteBotByIdAPI,
  getAllBotsAPI,
} from "../../services/data-flow-services";

interface CreateBot {
  timezone: string;
  name: string;
  language: string;
  avatarUrl: string;
}

const HomePage = () => {
  const [bots, setBot] = useState<Bot[]>();

  const handleDeleteBot = async (id: string) => {
    const result = await deleteBotByIdAPI(id);
    if (result) {
      const filterBotList = bots?.filter((bot) => bot.botId !== id);
      setBot(filterBotList);
    }
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

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
    name: string,
    avatarUrl: string
  ) => {
    event.preventDefault();
    const createBotInfo: CreateBot = {
      timezone: "UTC",
      name,
      language: "en",
      avatarUrl,
    };
    const result = await createBotsAPI(createBotInfo);
    if (result) {
      getAllBots();
    }
  };

  return (
    <React.Fragment>
      <Grid container>
        {bots?.map((bot) => (
          <Grid item sm={6} md={4} lg={3} key={bot.botId}>
            <BotInformationCard bot={bot} handleDelete={handleDeleteBot} />
          </Grid>
        ))}
        <Grid item sm={6} md={4} lg={3}>
          <CreateBotCard handleSubmit={handleSubmit} />
        </Grid>
      </Grid>
    </React.Fragment>
  );
};

export default HomePage;
