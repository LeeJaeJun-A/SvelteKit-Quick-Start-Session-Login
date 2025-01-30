import { env } from "$env/dynamic/public";
type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE";

interface Params {
  [key: string]: any;
}

type Callback = (response: any) => void;

const fastapi = (
  method: HTTPMethod,
  url: string,
  params: Params,
  successCallback?: Callback,
  failureCallback?: Callback,
  token?: string
) => {
  const baseUrl =
    env.PUBLIC_BACKEND_API_URL_PREFIX || "http://localhost:8000/api";

  let body: string | undefined;

  let _url = baseUrl + url;

  if (method === "GET") {
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(
        ([_, value]) => value !== null && value !== undefined
      )
    );

    if (Object.keys(filteredParams).length > 0) {
      const urlParams = new URLSearchParams(filteredParams).toString();
      _url += `?${urlParams}`;
    }
  } else {
    body = JSON.stringify(params);
  }

  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const options: RequestInit = {
    method,
    headers,
    body: method !== "GET" ? body : undefined,
    credentials: "include",
  };

  fetch(_url, options)
    .then(async (response) => {
      const json = await response.json();
      if (response.ok) {
        if (successCallback) {
          successCallback(json);
        }
      } else {
        if (failureCallback) {
          failureCallback(json);
        }
      }
    })
    .catch((error) => {
      console.log(error);
    });
};

export default fastapi;
