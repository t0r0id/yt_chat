import axios, { AxiosResponse, AxiosError } from "axios";
axios.defaults.withCredentials = true;

export class YtApiClient {
  public static async getUserChannels(): Promise<AxiosResponse> {
    let requestConfig = {
      method: "post",
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/onboard/user_channels`,
      data: {},
    };
    return await axios.request(requestConfig);
  }

  public static async removeUserChannel(
    channelId: string
  ): Promise<AxiosResponse> {
    let requestConfig = {
      data: { channel_id: channelId },
    };
    return await axios.request(requestConfig);
  }
}
