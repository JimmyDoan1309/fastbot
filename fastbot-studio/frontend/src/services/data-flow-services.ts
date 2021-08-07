import axiosInstance from "./axios-instance";

export const createBotsAPI = async (data: any) => {
  const url = "/bot/create";
  let result = false;
  await axiosInstance
    .post(url, data)
    .then(() => {
      result = true;
    })
    .catch((error) => console.error(error));
  return result;
};

export const getAllBotsAPI = async () => {
  const url = "/bot/";
  let result;
  await axiosInstance
    .get(url)
    .then((res) => {
      result = res.data;
    })
    .catch((error) => console.error(error));
  return result;
};

export const getBotByIdAPI = async (id: string) => {
  const url = `/bot/${id}`;
  let result;
  await axiosInstance
    .get(url)
    .then((res) => {
      result = res.data;
    })
    .catch((error) => console.error(error));
  return result as any;
};

export const updateBotByIdAPI = async (id: string) => {
  const data = null;
  const url = `/bot/${id}`;
  let result;
  await axiosInstance
    .put(url, data)
    .then((res) => {
      result = res.data;
    })
    .catch((error) => console.error(error));
  return result;
};

export const deleteBotByIdAPI = async (id: string) => {
  const url = `/bot/${id}`;
  let result = false;
  await axiosInstance
    .delete(url)
    .then(() => {
      result = true;
    })
    .catch((error) => console.error(error));
  return result;
};

export const saveBotDataAPI = async (id: string, data: any) => {
  const url = `/bot/${id}/data`;
  let result;
  await axiosInstance
    .post(url, data)
    .then((res) => {
      result = res.data;
    })
    .catch((error) => console.error(error));
  return result;
};
