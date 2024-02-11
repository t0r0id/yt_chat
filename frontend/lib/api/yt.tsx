import axios, { AxiosResponse, AxiosError } from "axios";
axios.defaults.withCredentials = true;

export class YtApiClient {
  public static async getChannels(): Promise<AxiosResponse> {
    let requestConfig = {
      method: "post",
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/onboard/channels`,
      data: {},
    };
    return await axios.request(requestConfig);
  }
}
